import 'package:flutter/material.dart';

class AlapApp extends StatelessWidget {
  const AlapApp({super.key});

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
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ALAP', style: TextStyle(fontWeight: FontWeight.w900, letterSpacing: -1)),
        actions: [IconButton(onPressed: () {}, icon: const Icon(Icons.account_circle_outlined))],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const SizedBox(height: 18),
          const Text('YOUR WORLD. YOUR CHARACTERS.', style: TextStyle(color: Color(0xFFC5F36A), letterSpacing: 2, fontSize: 11, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          const Text('Stories feel different\nwhen they know you.', style: TextStyle(fontSize: 36, height: 1.08, fontWeight: FontWeight.w800, letterSpacing: -1.5)),
          const SizedBox(height: 12),
          const Text('Discover original AI characters and create conversations that are yours to shape.', style: TextStyle(color: Colors.white70, height: 1.5)),
          const SizedBox(height: 30),
          const Text('PICK UP WHERE YOU LEFT OFF', style: TextStyle(color: Colors.white54, letterSpacing: 1.4, fontSize: 11)),
          const SizedBox(height: 12),
          const _EmptyState(icon: Icons.forum_outlined, title: 'Your conversations will live here', subtitle: 'Choose a character to start your first story.'),
          const SizedBox(height: 28),
          const Text('DISCOVER THE UNIVERSE', style: TextStyle(color: Colors.white54, letterSpacing: 1.4, fontSize: 11)),
          const SizedBox(height: 12),
          const _EmptyState(icon: Icons.auto_awesome, title: 'Characters are on their way', subtitle: 'The discovery catalogue will appear here when the service is connected.'),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        backgroundColor: const Color(0xFF141820),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.explore_outlined), label: 'Discover'),
          NavigationDestination(icon: Icon(Icons.add_circle_outline), label: 'Create'),
          NavigationDestination(icon: Icon(Icons.chat_bubble_outline), label: 'Chats'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Profile'),
        ],
        onDestinationSelected: (_) {},
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.icon, required this.title, required this.subtitle});
  final IconData icon;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(20),
    decoration: BoxDecoration(color: const Color(0xFF151A22), borderRadius: BorderRadius.circular(18), border: Border.all(color: Colors.white12)),
    child: Row(children: [
      Icon(icon, color: const Color(0xFFC5F36A), size: 28),
      const SizedBox(width: 16),
      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 5),
        Text(subtitle, style: const TextStyle(color: Colors.white60, fontSize: 12, height: 1.4)),
      ])),
    ]),
  );
}
