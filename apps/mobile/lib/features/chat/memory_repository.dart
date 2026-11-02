import '../../core/network/api_client.dart';

class MemoryRepository {
  MemoryRepository(this.api);
  final ApiClient api;
  Future<bool> preference(String id) async => (await api.dio.get('/characters/$id/memory/preference')).data['enabled'] as bool;
  Future<void> setEnabled(String id, bool enabled) async => api.dio.patch('/characters/$id/memory/preference', data: {'enabled': enabled});
  Future<List<Map<String, dynamic>>> list(String id) async => List<Map<String, dynamic>>.from((await api.dio.get('/characters/$id/memory')).data as List);
  Future<void> add(String id, String content) async => api.dio.post('/characters/$id/memory', data: {'content': content, 'category': 'preference', 'importance': 3});
  Future<void> delete(String id, String memoryId) async => api.dio.delete('/characters/$id/memory/$memoryId');
}
