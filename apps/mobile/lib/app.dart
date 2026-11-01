import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:audioplayers/audioplayers.dart';
import 'core/network/api_client.dart';
import 'features/auth/auth_repository.dart';
import 'features/auth/auth_screen.dart';
import 'features/characters/character_repository.dart';
import 'features/chat/conversation_repository.dart';
import 'features/memory/memory_repository.dart';
import 'features/media/media_repository.dart';

class AlapApp extends StatefulWidget {
  const AlapApp({super.key});
  @override
  State<AlapApp> createState() => _AlapAppState();
}

class _AlapAppState extends State<AlapApp> {
  late final FlutterSecureStorage _storage;
  late final ApiClient _api;
  late final AuthRepository _auth;
  late final CharacterRepository _characters;
  late final ConversationRepository _conversations;
  bool? _signedIn;

  @override
  void initState() {
    super.initState();
    _storage = const FlutterSecureStorage();
    _api = ApiClient(_storage);
    _auth = AuthRepository(_api, _storage);
    _characters = CharacterRepository(_api);
    _conversations = ConversationRepository(_api);
    _restore();
  }

  Future<void> _restore() async {
    final value = await _auth.hasSession();
    if (mounted) setState(() => _signedIn = value);
  }

  @override
  Widget build(BuildContext context) {
    const lime = Color(0xFFC5F36A);
    return MaterialApp(
      title: 'ALAP',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0C0E12),
        colorScheme: ColorScheme.fromSeed(seedColor: lime, brightness: Brightness.dark),
        useMaterial3: true,
        inputDecorationTheme: InputDecorationTheme(
          filled: true, fillColor: const Color(0xFF171C25),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide.none),
        ),
      ),
      home: _signedIn == null
          ? const Scaffold(body: Center(child: CircularProgressIndicator()))
          : _signedIn!
              ? HomeShell(auth: _auth, characters: _characters, conversations: _conversations, onLogout: () => setState(() => _signedIn = false))
              : AuthScreen(repository: _auth, onAuthenticated: () => setState(() => _signedIn = true)),
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key, required this.auth, required this.characters, required this.conversations, required this.onLogout});
  final AuthRepository auth;
  final CharacterRepository characters;
  final ConversationRepository conversations;
  final VoidCallback onLogout;

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;
  @override
  Widget build(BuildContext context) {
    final pages = [
      DiscoverScreen(characters: widget.characters, conversations: widget.conversations),
      CreateCharacterScreen(repository: widget.characters, conversations: widget.conversations),
      ChatsScreen(repository: widget.conversations),
      ProfileScreen(auth: widget.auth, onLogout: widget.onLogout),
    ];
    return Scaffold(
      appBar: AppBar(title: const Text('ALAP ✦', style: TextStyle(fontWeight: FontWeight.w900, letterSpacing: 1.5))),
      body: IndexedStack(index: _index, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (value) => setState(() => _index = value),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.explore_outlined), label: 'Discover'),
          NavigationDestination(icon: Icon(Icons.add_circle_outline), label: 'Create'),
          NavigationDestination(icon: Icon(Icons.chat_bubble_outline), label: 'Chats'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Profile'),
        ],
      ),
    );
  }
}

class DiscoverScreen extends StatefulWidget {
  const DiscoverScreen({super.key, required this.characters, required this.conversations});
  final CharacterRepository characters;
  final ConversationRepository conversations;
  @override
  State<DiscoverScreen> createState() => _DiscoverScreenState();
}

class _DiscoverScreenState extends State<DiscoverScreen> {
  late Future<List<Map<String, dynamic>>> _future;
  @override
  void initState() { super.initState(); _future = widget.characters.discover(); }
  void _reload() => setState(() => _future = widget.characters.discover());

  Future<void> _start(Map<String, dynamic> character) async {
    try {
      final conversation = await widget.conversations.create(character['id'] as String);
      if (!mounted) return;
      Navigator.of(context).push(MaterialPageRoute(builder: (_) => ChatScreen(repository: widget.conversations, conversation: conversation)));
    } catch (_) {
      if (mounted) _showError(context, 'Could not start this conversation.');
    }
  }

  Future<void> _report(Map<String, dynamic> character) async {
    final details = TextEditingController();
    var reason = 'other';
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Report character'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<String>(
                initialValue: reason,
                decoration: const InputDecoration(labelText: 'Reason'),
                items: const [
                  DropdownMenuItem(value: 'sexual_content', child: Text('Sexual content')),
                  DropdownMenuItem(value: 'minor_safety', child: Text('Minor safety')),
                  DropdownMenuItem(value: 'violence', child: Text('Violence or harm')),
                  DropdownMenuItem(value: 'harassment', child: Text('Harassment')),
                  DropdownMenuItem(value: 'impersonation', child: Text('Impersonation')),
                  DropdownMenuItem(value: 'spam', child: Text('Spam')),
                  DropdownMenuItem(value: 'other', child: Text('Other')),
                ],
                onChanged: (value) => setDialogState(() => reason = value ?? 'other'),
              ),
              const SizedBox(height: 12),
              TextField(controller: details, maxLines: 3, maxLength: 2000, decoration: const InputDecoration(labelText: 'Additional details (optional)')),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
            FilledButton(onPressed: () => Navigator.pop(dialogContext, {'reason': reason, 'details': details.text}), child: const Text('Submit report')),
          ],
        ),
      ),
    );
    final detailText = details.text;
    details.dispose();
    if (result == null || !mounted) return;
    try {
      await widget.characters.report(character['id'] as String, reason: result['reason']!, details: detailText);
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Report submitted. Thank you for helping keep ALAP safe.')));
    } catch (_) {
      if (mounted) _showError(context, 'Could not submit this report. You may already have an open report.');
    }
  }

  @override
  Widget build(BuildContext context) => RefreshIndicator(
    onRefresh: () async => _reload(),
    child: FutureBuilder<List<Map<String, dynamic>>>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
        if (snapshot.hasError) return _RetryState(message: 'Could not load characters. Check your connection.', onRetry: _reload);
        final items = snapshot.data ?? [];
        if (items.isEmpty) return ListView(padding: const EdgeInsets.all(24), children: const [
          SizedBox(height: 50), Text('YOUR WORLD. YOUR CHARACTERS.', style: TextStyle(color: Color(0xFFC5F36A), letterSpacing: 2, fontSize: 11, fontWeight: FontWeight.bold)),
          SizedBox(height: 18), Text('Find a story\nthat feels like yours.', style: TextStyle(fontSize: 34, height: 1.1, fontWeight: FontWeight.w800)),
          SizedBox(height: 12), Text('Published characters will appear here after moderation. You can create your own character in the Create tab.', style: TextStyle(color: Colors.white60, height: 1.5)),
        ]);
        return ListView(padding: const EdgeInsets.all(18), children: [
          const Text('DISCOVER', style: TextStyle(color: Color(0xFFC5F36A), letterSpacing: 2, fontSize: 11, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          for (final item in items) Card(
            child: ListTile(
              contentPadding: const EdgeInsets.all(16),
              leading: const CircleAvatar(backgroundColor: Color(0xFF293342), child: Icon(Icons.auto_awesome, color: Color(0xFFC5F36A))),
              title: Text(item['name'] as String, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Padding(padding: const EdgeInsets.only(top: 6), child: Text(item['description'] as String? ?? '', maxLines: 3, overflow: TextOverflow.ellipsis)),
              trailing: IconButton(
                tooltip: 'Report character',
                icon: const Icon(Icons.flag_outlined),
                onPressed: () => _report(item),
              ),
              onTap: () => _start(item),
            ),
          ),
        ]);
      },
    ),
  );
}

class CreateCharacterScreen extends StatefulWidget {
  const CreateCharacterScreen({super.key, required this.repository, required this.conversations});
  final CharacterRepository repository;
  final ConversationRepository conversations;
  @override
  State<CreateCharacterScreen> createState() => _CreateCharacterScreenState();
}

class _CreateCharacterScreenState extends State<CreateCharacterScreen> {
  final _name = TextEditingController();
  final _description = TextEditingController();
  final _greeting = TextEditingController();
  final _personality = TextEditingController();
  bool _busy = false;

  @override
  void dispose() { _name.dispose(); _description.dispose(); _greeting.dispose(); _personality.dispose(); super.dispose(); }

  Future<void> _create() async {
    if (_name.text.trim().length < 2) { _showError(context, 'Character name must be at least 2 characters.'); return; }
    setState(() => _busy = true);
    try {
      final character = await widget.repository.create(
        name: _name.text.trim(), description: _description.text.trim(), greeting: _greeting.text.trim(),
        personality: _personality.text.trim().isEmpty ? {} : {'traits': _personality.text.trim()},
        visibility: 'private',
      );
      if (!mounted) return;
      _name.clear(); _description.clear(); _greeting.clear(); _personality.clear();
      try {
        final conversation = await widget.conversations.create(character['id'] as String);
        if (!mounted) return;
        Navigator.of(context).push(MaterialPageRoute(builder: (_) => ChatScreen(repository: widget.conversations, conversation: conversation)));
      } catch (_) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Character created, but chat could not be started.')));
      }
    } catch (_) {
      if (mounted) _showError(context, 'Character could not be created.');
    } finally { if (mounted) setState(() => _busy = false); }
  }

  @override
  Widget build(BuildContext context) => ListView(padding: const EdgeInsets.all(20), children: [
    const Text('CREATE A CHARACTER', style: TextStyle(color: Color(0xFFC5F36A), letterSpacing: 2, fontSize: 11, fontWeight: FontWeight.bold)),
    const SizedBox(height: 14), const Text('Bring someone new to life.', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800)),
    const SizedBox(height: 22),
    TextField(controller: _name, decoration: const InputDecoration(labelText: 'Character name')),
    const SizedBox(height: 12), TextField(controller: _description, maxLines: 3, decoration: const InputDecoration(labelText: 'Description')),
    const SizedBox(height: 12), TextField(controller: _personality, maxLines: 2, decoration: const InputDecoration(labelText: 'Personality and traits')),
    const SizedBox(height: 12), TextField(controller: _greeting, maxLines: 3, decoration: const InputDecoration(labelText: 'Opening greeting')),
    const SizedBox(height: 18), FilledButton(onPressed: _busy ? null : _create, child: Padding(padding: const EdgeInsets.all(14), child: _busy ? const CircularProgressIndicator() : const Text('Create character'))),
  ]);
}

class ChatsScreen extends StatefulWidget {
  const ChatsScreen({super.key, required this.repository});
  final ConversationRepository repository;
  @override
  State<ChatsScreen> createState() => _ChatsScreenState();
}

class _ChatsScreenState extends State<ChatsScreen> {
  late Future<List<Map<String, dynamic>>> _future;
  @override
  void initState() { super.initState(); _future = widget.repository.api.dio.get('/conversations').then((r) => List<Map<String, dynamic>>.from(r.data as List)); }
  @override
  Widget build(BuildContext context) => FutureBuilder<List<Map<String, dynamic>>>(
    future: _future,
    builder: (context, snapshot) {
      if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
      if (snapshot.hasError) return _RetryState(message: 'Could not load conversations.', onRetry: () => setState(() => _future = widget.repository.api.dio.get('/conversations').then((r) => List<Map<String, dynamic>>.from(r.data as List))));
      final items = snapshot.data ?? [];
      if (items.isEmpty) return const Center(child: Text('Your conversations will appear here.', style: TextStyle(color: Colors.white60)));
      return ListView(children: [for (final item in items) ListTile(
        leading: const CircleAvatar(child: Icon(Icons.forum_outlined)),
        title: Text(item['title'] as String),
        subtitle: const Text('Continue conversation'),
        onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ChatScreen(repository: widget.repository, conversation: item))),
      )]);
    },
  );
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key, required this.repository, required this.conversation});
  final ConversationRepository repository;
  final Map<String, dynamic> conversation;
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _input = TextEditingController();
  final _scroll = ScrollController();
  List<Map<String, dynamic>> _messages = [];
  bool _loading = true;
  bool _sending = false;
  final List<Map<String, dynamic>> _generatedMedia = [];
  final AudioPlayer _audioPlayer = AudioPlayer();
  String get _id => widget.conversation['id'] as String;

  @override
  void initState() { super.initState(); _load(); }
  @override
  void dispose() { _input.dispose(); _scroll.dispose(); unawaited(_audioPlayer.dispose()); super.dispose(); }

  Future<void> _load() async {
    try { final data = await widget.repository.messages(_id); if (mounted) setState(() { _messages = data; _loading = false; }); }
    catch (_) { if (mounted) setState(() => _loading = false); }
  }

  Future<String?> _askForText(String title, String hint) async {
    final controller = TextEditingController();
    final value = await showDialog<String>(context: context, builder: (ctx) => AlertDialog(
      title: Text(title), content: TextField(controller: controller, autofocus: true, maxLines: 4, maxLength: 1000, decoration: InputDecoration(hintText: hint)),
      actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(ctx, controller.text.trim()), child: const Text('Generate'))],
    ));
    controller.dispose();
    return value;
  }
  Future<void> _generateImage() async {
    final prompt = await _askForText('Create an image', 'Describe the image…');
    if (prompt == null || prompt.length < 4 || !mounted) return;
    try { final item = await MediaRepository(widget.repository.api).image(prompt, _id); if (mounted) setState(() => _generatedMedia.insert(0, item)); }
    catch (_) { if (mounted) _showError(context, 'Image generation failed. Check media budget and try again.'); }
  }
  Future<void> _generateVoice() async {
    final text = await _askForText('Generate character voice', 'Enter the words to speak…');
    if (text == null || text.isEmpty || !mounted) return;
    try { final item = await MediaRepository(widget.repository.api).voice(text, _id); if (mounted) setState(() => _generatedMedia.insert(0, item)); }
    catch (_) { if (mounted) _showError(context, 'Voice generation failed. Check media budget and try again.'); }
  }

  Future<void> _send() async {
    final text = _input.text.trim();
    if (text.isEmpty || _sending) return;
    _input.clear();
    setState(() => _sending = true);
    try {
      final turn = await widget.repository.send(_id, text);
      if (mounted) setState(() => _messages.addAll([
        Map<String, dynamic>.from(turn['user_message'] as Map),
        Map<String, dynamic>.from(turn['assistant_message'] as Map),
      ]));
      if (mounted && _messages.length >= 6 && _messages.length % 6 == 0) {
        try {
          final memory = MemoryRepository(widget.repository.api);
          if (await memory.consent()) await memory.extract(_id);
        } catch (_) { /* Optional memory extraction must never block a successful chat turn. */ }
      }
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scroll.hasClients) _scroll.animateTo(_scroll.position.maxScrollExtent, duration: const Duration(milliseconds: 250), curve: Curves.easeOut);
      });
    } catch (_) {
      if (mounted) { _input.text = text; _showError(context, 'Message could not be sent. Check AI provider configuration.'); }
    } finally { if (mounted) setState(() => _sending = false); }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(widget.conversation['title'] as String? ?? 'Conversation')),
    body: Column(children: [
      Expanded(child: _loading ? const Center(child: CircularProgressIndicator()) : ListView(
        controller: _scroll, padding: const EdgeInsets.all(16), children: [
          for (final media in _generatedMedia) Card(child: Padding(padding: const EdgeInsets.all(8), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            if (media['kind'] == 'image') Image.network(media['url'] as String, errorBuilder: (_, __, ___) => const Text('Image link expired; generate a fresh image.')),
            if (media['kind'] == 'voice') Row(children: [const Icon(Icons.graphic_eq), const SizedBox(width: 8), const Expanded(child: Text('Generated voice audio')), IconButton(onPressed: () => _audioPlayer.play(UrlSource(media['url'] as String)), icon: const Icon(Icons.play_circle_outline))]),
          ]))),
          for (final message in _messages) Align(
            alignment: message['role'] == 'user' ? Alignment.centerRight : Alignment.centerLeft,
            child: Container(
              constraints: const BoxConstraints(maxWidth: 320),
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(color: message['role'] == 'user' ? const Color(0xFF344329) : const Color(0xFF1A202A), borderRadius: BorderRadius.circular(16)),
              child: Text(message['content'] as String),
            ),
          ),
          if (_sending) const Align(alignment: Alignment.centerLeft, child: Padding(padding: EdgeInsets.all(12), child: Text('Thinking…', style: TextStyle(color: Colors.white54)))),
        ],
      )),
      SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(8, 8, 8, 12), child: Row(children: [
        IconButton(tooltip: 'Generate image', onPressed: _sending ? null : _generateImage, icon: const Icon(Icons.image_outlined)),
        IconButton(tooltip: 'Generate voice', onPressed: _sending ? null : _generateVoice, icon: const Icon(Icons.record_voice_over_outlined)),
        Expanded(child: TextField(controller: _input, minLines: 1, maxLines: 4, decoration: const InputDecoration(hintText: 'Write a message…'))),
        const SizedBox(width: 8), IconButton.filled(onPressed: _sending ? null : _send, icon: const Icon(Icons.send)),
      ]))),
    ]),
  );
}

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key, required this.auth, required this.onLogout});
  final AuthRepository auth;
  final VoidCallback onLogout;
  Future<void> _exportData(BuildContext context) async {
    try {
      final data = await auth.exportData();
      await Clipboard.setData(ClipboardData(text: const JsonEncoder.withIndent('  ').convert(data)));
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Your account export JSON was copied to the clipboard.')));
      }
    } catch (_) {
      if (context.mounted) _showError(context, 'Could not export your account data.');
    }
  }

  Future<void> _deleteAccount(BuildContext context) async {
    final controller = TextEditingController();
    final password = await showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Delete account?'),
        content: TextField(
          controller: controller,
          obscureText: true,
          decoration: const InputDecoration(labelText: 'Confirm your password'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, controller.text),
            child: const Text('Permanently delete'),
          ),
        ],
      ),
    );
    controller.dispose();
    if (password == null || password.isEmpty || !context.mounted) return;
    try {
      await auth.deleteAccount(password);
      if (context.mounted) onLogout();
    } catch (_) {
      if (context.mounted) _showError(context, 'Account deletion failed. Check your password and try again.');
    }
  }

  @override
  Widget build(BuildContext context) => ListView(padding: const EdgeInsets.all(20), children: [
    const CircleAvatar(radius: 32, child: Icon(Icons.person_outline, size: 30)),
    const SizedBox(height: 18), const Text('Your ALAP account', textAlign: TextAlign.center, style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
    const SizedBox(height: 24),
    ListTile(leading: const Icon(Icons.psychology_outlined), title: const Text('AI memory'), subtitle: const Text('Opt in, review, and delete what ALAP remembers.'), onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => MemorySettingsScreen(repository: MemoryRepository(auth.api))))),
    ListTile(leading: const Icon(Icons.logout), title: const Text('Sign out'), onTap: () async { await auth.logout(); onLogout(); }),
    ListTile(leading: const Icon(Icons.download_outlined), title: const Text('Export my data'), subtitle: const Text('Copy your account, characters and conversations as JSON.'), onTap: () => _exportData(context)),
    ListTile(
      leading: const Icon(Icons.delete_outline, color: Colors.redAccent),
      title: const Text('Delete account and data', style: TextStyle(color: Colors.redAccent)),
      subtitle: const Text('Permanently delete your account, characters and conversations.'),
      onTap: () => _deleteAccount(context),
    ),
  ]);
}


class MemorySettingsScreen extends StatefulWidget {
  const MemorySettingsScreen({super.key, required this.repository});
  final MemoryRepository repository;
  @override
  State<MemorySettingsScreen> createState() => _MemorySettingsScreenState();
}
class _MemorySettingsScreenState extends State<MemorySettingsScreen> {
  bool? _enabled;
  bool _busy = false;
  List<Map<String, dynamic>> _items = [];
  @override
  void initState() { super.initState(); _load(); }
  Future<void> _load() async {
    try { final enabled = await widget.repository.consent(); final items = await widget.repository.list(); if (mounted) setState(() { _enabled = enabled; _items = items; }); }
    catch (_) { if (mounted) _showError(context, 'Could not load AI memory settings.'); }
  }
  Future<void> _toggle(bool value) async {
    setState(() => _busy = true);
    try { await widget.repository.setConsent(value); if (mounted) setState(() => _enabled = value); }
    catch (_) { if (mounted) _showError(context, 'Could not update memory consent.'); }
    finally { if (mounted) setState(() => _busy = false); }
  }
  Future<void> _add() async {
    final controller = TextEditingController();
    final content = await showDialog<String>(context: context, builder: (ctx) => AlertDialog(
      title: const Text('Add a memory'), content: TextField(controller: controller, autofocus: true, maxLength: 500, maxLines: 3, decoration: const InputDecoration(hintText: 'Example: I prefer concise explanations. Do not save passwords or sensitive details.')),
      actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(ctx, controller.text.trim()), child: const Text('Save'))],
    ));
    controller.dispose();
    if (content == null || content.length < 3) return;
    try { await widget.repository.add(content, 'preference'); await _load(); }
    catch (_) { if (mounted) _showError(context, 'Could not save this memory.'); }
  }
  Future<void> _delete(String id) async {
    try { await widget.repository.delete(id); await _load(); }
    catch (_) { if (mounted) _showError(context, 'Could not delete this memory.'); }
  }
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('AI memory')),
    floatingActionButton: _enabled == true ? FloatingActionButton(onPressed: _add, child: const Icon(Icons.add)) : null,
    body: _enabled == null ? const Center(child: CircularProgressIndicator()) : ListView(padding: const EdgeInsets.all(16), children: [
      SwitchListTile(value: _enabled!, onChanged: _busy ? null : _toggle, title: const Text('Allow ALAP to remember'), subtitle: const Text('When enabled, ALAP can extract non-sensitive preferences and context from your conversations. You can review and delete memories at any time.')),
      if (_enabled!) ...[
        const Text('Saved memories', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        if (_items.isEmpty) const Padding(padding: EdgeInsets.all(16), child: Text('No saved memories yet.')),
        for (final item in _items) Card(child: ListTile(title: Text(item['content'] as String), subtitle: Text(item['category'] as String), trailing: IconButton(icon: const Icon(Icons.delete_outline), onPressed: () => _delete(item['id'] as String)))),
        TextButton.icon(onPressed: _items.isEmpty ? null : () async { await widget.repository.clear(); await _load(); }, icon: const Icon(Icons.delete_sweep_outlined), label: const Text('Delete all memories')),
      ] else const Padding(padding: EdgeInsets.all(12), child: Text('Memory is off. Existing memories are retained but are not used in chats. Turn it on to use them again.')),
    ]),
  );
}

class _RetryState extends StatelessWidget {
  const _RetryState({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) => Center(child: Padding(padding: const EdgeInsets.all(24), child: Column(mainAxisSize: MainAxisSize.min, children: [
    Text(message, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white60)),
    const SizedBox(height: 12), OutlinedButton(onPressed: onRetry, child: const Text('Try again')),
  ])));
}

void _showError(BuildContext context, String message) {
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
}
