import 'package:flutter/material.dart';
import 'auth_repository.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key, required this.repository, required this.onAuthenticated});
  final AuthRepository repository;
  final VoidCallback onAuthenticated;

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _form = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _name = TextEditingController();
  bool _register = false;
  bool _adult = false;
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _email.dispose(); _password.dispose(); _name.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_form.currentState!.validate()) return;
    if (_register && !_adult) {
      setState(() => _error = 'You must confirm the age requirement to register.');
      return;
    }
    setState(() { _busy = true; _error = null; });
    try {
      if (_register) {
        await widget.repository.register(_email.text.trim(), _password.text, _name.text.trim(), _adult);
      } else {
        await widget.repository.login(_email.text.trim(), _password.text);
      }
      if (mounted) widget.onAuthenticated();
    } catch (_) {
      if (mounted) setState(() => _error = 'Unable to sign in or create the account. Check your details and try again.');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(child: Center(child: SingleChildScrollView(padding: const EdgeInsets.all(24), child: ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 440),
      child: Form(key: _form, child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        const Text('ALAP ✦', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, letterSpacing: 2)),
        const SizedBox(height: 54),
        Text(_register ? 'Create your account' : 'Welcome back', style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w800)),
        const SizedBox(height: 8),
        const Text('Step into a universe of characters and stories.', style: TextStyle(color: Colors.white60)),
        const SizedBox(height: 28),
        if (_register) ...[
          TextFormField(controller: _name, decoration: const InputDecoration(labelText: 'Display name'), validator: (v) => (v == null || v.trim().isEmpty) ? 'Enter a display name' : null),
          const SizedBox(height: 14),
        ],
        TextFormField(controller: _email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'Email address'), validator: (v) => (v == null || !v.contains('@')) ? 'Enter a valid email' : null),
        const SizedBox(height: 14),
        TextFormField(controller: _password, obscureText: true, decoration: const InputDecoration(labelText: 'Password'), validator: (v) => (v == null || v.length < (_register ? 12 : 1)) ? (_register ? 'Use at least 12 characters' : 'Enter your password') : null),
        if (_register) CheckboxListTile(value: _adult, onChanged: (v) => setState(() => _adult = v ?? false), contentPadding: EdgeInsets.zero, title: const Text('I confirm that I meet the minimum age requirement', style: TextStyle(fontSize: 12))),
        if (_error != null) Padding(padding: const EdgeInsets.only(bottom: 12), child: Text(_error!, style: const TextStyle(color: Colors.redAccent))),
        const SizedBox(height: 12),
        FilledButton(onPressed: _busy ? null : _submit, child: Padding(padding: const EdgeInsets.all(14), child: _busy ? const CircularProgressIndicator() : Text(_register ? 'Create account' : 'Sign in'))),
        TextButton(onPressed: _busy ? null : () => setState(() { _register = !_register; _error = null; }), child: Text(_register ? 'Already have an account? Sign in' : 'New to ALAP? Create an account')),
      ])),
    )))),
  );
}
