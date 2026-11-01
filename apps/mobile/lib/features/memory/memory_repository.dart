import '../../core/network/api_client.dart';

class MemoryRepository {
  MemoryRepository(this.api);
  final ApiClient api;
  Future<bool> consent() async => (await api.dio.get('/memory/consent')).data['enabled'] == true;
  Future<bool> setConsent(bool enabled) async => (await api.dio.put('/memory/consent', data: {'enabled': enabled})).data['enabled'] == true;
  Future<List<Map<String, dynamic>>> list() async => List<Map<String, dynamic>>.from((await api.dio.get('/memory')).data as List);
  Future<void> add(String content, String category) async { await api.dio.post('/memory', data: {'content': content, 'category': category}); }
  Future<void> delete(String id) async { await api.dio.delete('/memory/$id'); }
  Future<void> clear() async { await api.dio.delete('/memory'); }
  Future<void> extract(String conversationId) async { await api.dio.post('/memory/extract/$conversationId'); }
}
