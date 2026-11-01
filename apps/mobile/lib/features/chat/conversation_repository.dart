import '../../core/network/api_client.dart';

class ConversationRepository {
  ConversationRepository(this.api);
  final ApiClient api;

  Future<Map<String, dynamic>> create(String characterId) async {
    final response = await api.dio.post('/conversations', data: {'character_id': characterId});
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<List<Map<String, dynamic>>> messages(String conversationId) async {
    final response = await api.dio.get('/conversations/' + conversationId + '/messages');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  Future<Map<String, dynamic>> send(String conversationId, String content) async {
    final response = await api.dio.post('/conversations/' + conversationId + '/messages', data: {'content': content});
    return Map<String, dynamic>.from(response.data as Map);
  }
}
