import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import '../../core/network/api_client.dart';
import 'memory_repository.dart';
import 'media_repository.dart';

class ChatToolsScreen extends StatefulWidget {
  const ChatToolsScreen({super.key, required this.api, required this.characterId, required this.lastAssistantText});
  final ApiClient api;
  final String characterId;
  final String lastAssistantText;
  @override
  State<ChatToolsScreen> createState() => _ChatToolsScreenState();
}

class _ChatToolsScreenState extends State<ChatToolsScreen> {
  late final MemoryRepository _memory = MemoryRepository(widget.api);
  late final MediaRepository _media = MediaRepository(widget.api);
  final AudioPlayer _player = AudioPlayer();
  final TextEditingController _imagePrompt = TextEditingController();
  final TextEditingController _speechText = TextEditingController();
  bool _memoryEnabled = false, _loading = true, _busy = false;
  List<Map<String, dynamic>> _memories = [];
  String? _imageUrl, _audioUrl;

  @override
  void initState() { super.initState(); _speechText.text = widget.lastAssistantText; _loadMemory(); }
  @override
  void dispose() { _player.dispose(); _imagePrompt.dispose(); _speechText.dispose(); super.dispose(); }

  Future<void> _loadMemory() async {
    try {
      final enabled = await _memory.preference(widget.characterId);
      final items = await _memory.list(widget.characterId);
      if (mounted) setState(() { _memoryEnabled = enabled; _memories = items; _loading = false; });
    } catch (_) { if (mounted) setState(() => _loading = false); }
  }

  Future<void> _toggleMemory(bool enabled) async {
    try {
      await _memory.setEnabled(widget.characterId, enabled);
      if (mounted) setState(() { _memoryEnabled = enabled; if (!enabled) _memories = []; });
      _notice(enabled ? 'Long-term memory enabled.' : 'Memory disabled and saved memories cleared.');
    } catch (_) { if (mounted) _notice('Could not update memory settings. Check server encryption configuration.'); }
  }

  Future<void> _addMemory() async {
    final controller = TextEditingController();
    final value = await showDialog<String>(context: context, builder: (context) => AlertDialog(
      title: const Text('Add a memory'),
      content: TextField(controller: controller, autofocus: true, maxLength: 240, minLines: 2, maxLines: 4, decoration: const InputDecoration(hintText: 'A preference or detail to remember')),
      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context, controller.text.trim()), child: const Text('Save'))],
    ));
    controller.dispose();
    if (value == null || value.length < 4) return;
    try { await _memory.add(widget.characterId, value); await _loadMemory(); }
    catch (_) { if (mounted) _notice('Memory could not be saved.'); }
  }

  Future<void> _deleteMemory(String id) async {
    try { await _memory.delete(widget.characterId, id); await _loadMemory(); }
    catch (_) { if (mounted) _notice('Could not delete this memory.'); }
  }

  Future<void> _generateImage() async {
    final prompt = _imagePrompt.text.trim();
    if (prompt.length < 5 || _busy) return;
    setState(() => _busy = true);
    try { final result = await _media.generateImage(prompt); if (mounted) setState(() => _imageUrl = result['url'] as String); }
    catch (_) { if (mounted) _notice('Image generation failed. Check provider, quota and storage settings.'); }
    finally { if (mounted) setState(() => _busy = false); }
  }

  Future<void> _generateSpeech() async {
    final text = _speechText.text.trim();
    if (text.isEmpty || _busy) return;
    setState(() => _busy = true);
    try {
      final result = await _media.generateSpeech(text);
      final url = result['url'] as String;
      await _player.setUrl(url);
      if (mounted) setState(() => _audioUrl = url);
      await _player.play();
    } catch (_) { if (mounted) _notice('Voice generation failed. Check provider, quota and storage settings.'); }
    finally { if (mounted) setState(() => _busy = false); }
  }

  void _notice(String value) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(value)));

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Conversation tools')),
    body: ListView(padding: const EdgeInsets.all(18), children: [
      Text('Long-term memory', style: Theme.of(context).textTheme.titleLarge),
      const SizedBox(height: 6),
      const Text('Memory is private to your account. Automatic memory is opt-in; inspect and delete saved items here.'),
      if (_loading) const LinearProgressIndicator(),
      SwitchListTile(contentPadding: EdgeInsets.zero, title: const Text('Remember useful details'), subtitle: const Text('Turning this off clears saved memories across characters.'), value: _memoryEnabled, onChanged: _loading ? null : _toggleMemory),
      if (_memoryEnabled) ...[
        Row(children: [const Expanded(child: Text('Saved memories')), TextButton.icon(onPressed: _addMemory, icon: const Icon(Icons.add), label: const Text('Add'))]),
        if (_memories.isEmpty) const Text('No memories saved yet.'),
        for (final item in _memories) ListTile(contentPadding: EdgeInsets.zero, title: Text(item['content'] as String), subtitle: Text('${item['category']} · importance ${item['importance']}'), trailing: IconButton(icon: const Icon(Icons.delete_outline), onPressed: () => _deleteMemory(item['id'] as String))),
      ],
      const Divider(height: 32),
      Text('Create an image', style: Theme.of(context).textTheme.titleLarge),
      const SizedBox(height: 8),
      TextField(controller: _imagePrompt, minLines: 2, maxLines: 4, maxLength: 1200, decoration: const InputDecoration(border: OutlineInputBorder(), hintText: 'Describe the image to generate')),
      FilledButton.icon(onPressed: _busy ? null : _generateImage, icon: const Icon(Icons.image_outlined), label: const Text('Generate image')),
      if (_imageUrl != null) ...[const SizedBox(height: 12), ClipRRect(borderRadius: BorderRadius.circular(12), child: Image.network(_imageUrl!, errorBuilder: (_, __, ___) => const Text('Image link expired. Generate it again.')))],
      const Divider(height: 32),
      Text('Voice generation', style: Theme.of(context).textTheme.titleLarge),
      const SizedBox(height: 8),
      TextField(controller: _speechText, minLines: 3, maxLines: 6, maxLength: 4000, decoration: const InputDecoration(border: OutlineInputBorder(), hintText: 'Text to speak')),
      FilledButton.icon(onPressed: _busy ? null : _generateSpeech, icon: const Icon(Icons.record_voice_over), label: const Text('Generate and play voice')),
      if (_audioUrl != null) TextButton.icon(onPressed: () async { if (_player.playing) { await _player.pause(); } else { await _player.play(); } }, icon: Icon(_player.playing ? Icons.pause : Icons.play_arrow), label: const Text('Play / pause generated audio')),
      if (_busy) const Padding(padding: EdgeInsets.all(12), child: Center(child: CircularProgressIndicator())),
    ]),
  );
}
