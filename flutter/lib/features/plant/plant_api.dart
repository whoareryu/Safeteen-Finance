// fastapi/apps/plant 백엔드 클라이언트. www/lib/my-plants-api.ts, www/lib/plant-api.ts와
// 동일한 엔드포인트·필드명을 사용한다 (실제 마운트 경로는 fastapi/apps/plant/adapter/inbound/api/__init__.py 참고).
//
// 게스트 모드: 모바일에는 아직 로그인이 없어 owner_user_id를 보내지 않는다 — 백엔드도
// 이 값을 선택적으로 취급하므로, 등록된 모든 사용자의 식물이 함께 조회된다.

import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

import 'plant_models.dart';

const _kPlantApiBase = 'https://api.whoareryu.cloud/api/plant';

class PlantApiException implements Exception {
  PlantApiException(this.message);
  final String message;

  @override
  String toString() => message;
}

T _parseOrThrow<T>(
  http.Response res,
  T Function(dynamic json) parse,
) {
  dynamic decoded;
  try {
    decoded = res.body.isEmpty ? null : json.decode(res.body);
  } catch (_) {
    decoded = null;
  }
  if (res.statusCode < 200 || res.statusCode >= 300) {
    final detail = decoded is Map ? decoded['detail'] : null;
    throw PlantApiException(detail is String ? detail : 'HTTP ${res.statusCode}');
  }
  return parse(decoded);
}

Future<MyPlant> registerMyPlant({
  required String region,
  String? speciesName,
  Uint8List? photoBytes,
  String? photoFilename,
}) async {
  final req = http.MultipartRequest('POST', Uri.parse('$_kPlantApiBase/my-plants'));
  req.fields['region'] = region;
  if (speciesName != null && speciesName.isNotEmpty) {
    req.fields['species_name'] = speciesName;
  }
  if (photoBytes != null) {
    req.files.add(http.MultipartFile.fromBytes(
      'file',
      photoBytes,
      filename: photoFilename ?? 'photo.jpg',
    ));
  }
  final streamed = await req.send().timeout(const Duration(seconds: 30));
  final res = await http.Response.fromStream(streamed);
  return _parseOrThrow(res, (j) => MyPlant.fromJson(j as Map<String, dynamic>));
}

Future<List<MyPlant>> listMyPlants() async {
  final res = await http
      .get(Uri.parse('$_kPlantApiBase/my-plants'))
      .timeout(const Duration(seconds: 15));
  return _parseOrThrow(res, (j) {
    final list = j as List<dynamic>;
    return list.map((e) => MyPlant.fromJson(e as Map<String, dynamic>)).toList();
  });
}

Future<MyPlant> getMyPlant(int plantId) async {
  final res = await http
      .get(Uri.parse('$_kPlantApiBase/my-plants/$plantId'))
      .timeout(const Duration(seconds: 15));
  return _parseOrThrow(res, (j) => MyPlant.fromJson(j as Map<String, dynamic>));
}

Future<DiagnosisResult> uploadPlantPhoto({
  required Uint8List photoBytes,
  required String region,
  required String photoFilename,
}) async {
  final req = http.MultipartRequest(
    'POST',
    Uri.parse('$_kPlantApiBase/diagnosis/upload'),
  );
  req.fields['region'] = region;
  req.files.add(http.MultipartFile.fromBytes('file', photoBytes, filename: photoFilename));
  final streamed = await req.send().timeout(const Duration(seconds: 30));
  final res = await http.Response.fromStream(streamed);
  return _parseOrThrow(res, (j) => DiagnosisResult.fromJson(j as Map<String, dynamic>));
}

Future<DiagnosisResult> fetchDiagnosis(int id) async {
  final res = await http
      .get(Uri.parse('$_kPlantApiBase/diagnosis/$id'))
      .timeout(const Duration(seconds: 15));
  return _parseOrThrow(res, (j) => DiagnosisResult.fromJson(j as Map<String, dynamic>));
}

Future<CareGuideResult> generateCareGuide(int diagnosisId) async {
  final res = await http
      .post(Uri.parse('$_kPlantApiBase/diagnosis/$diagnosisId/care-guide'))
      .timeout(const Duration(seconds: 30));
  return _parseOrThrow(res, (j) => CareGuideResult.fromJson(j as Map<String, dynamic>));
}

Future<CheckinResult> checkinMyPlant(int plantId, Uint8List photoBytes, String photoFilename) async {
  final req = http.MultipartRequest(
    'POST',
    Uri.parse('$_kPlantApiBase/my-plants/$plantId/checkin'),
  );
  req.files.add(http.MultipartFile.fromBytes('file', photoBytes, filename: photoFilename));
  final streamed = await req.send().timeout(const Duration(seconds: 30));
  final res = await http.Response.fromStream(streamed);
  return _parseOrThrow(res, (j) => CheckinResult.fromJson(j as Map<String, dynamic>));
}

Future<List<CheckinHistoryItem>> listCheckins(int plantId) async {
  final res = await http
      .get(Uri.parse('$_kPlantApiBase/my-plants/$plantId/checkins'))
      .timeout(const Duration(seconds: 15));
  return _parseOrThrow(
    res,
    (j) => (j as List<dynamic>)
        .map((e) => CheckinHistoryItem.fromJson(e as Map<String, dynamic>))
        .toList(),
  );
}

Future<List<PlantBadge>> listBadges(int plantId) async {
  final res = await http
      .get(Uri.parse('$_kPlantApiBase/my-plants/$plantId/badges'))
      .timeout(const Duration(seconds: 15));
  return _parseOrThrow(
    res,
    (j) =>
        (j as List<dynamic>).map((e) => PlantBadge.fromJson(e as Map<String, dynamic>)).toList(),
  );
}

Future<List<LeaderboardEntry>> getLeaderboard({int limit = 20}) async {
  final res = await http
      .get(Uri.parse('$_kPlantApiBase/leaderboard?limit=$limit'))
      .timeout(const Duration(seconds: 15));
  return _parseOrThrow(
    res,
    (j) => (j as List<dynamic>)
        .map((e) => LeaderboardEntry.fromJson(e as Map<String, dynamic>))
        .toList(),
  );
}

Future<WeatherSnapshot> fetchWeatherStatus(String region) async {
  final res = await http
      .get(Uri.parse('$_kPlantApiBase/weather/current?region=${Uri.encodeComponent(region)}'))
      .timeout(const Duration(seconds: 15));
  return _parseOrThrow(res, (j) => WeatherSnapshot.fromJson(j as Map<String, dynamic>));
}

Future<List<NotificationEvent>> fetchNotifications(int plantId) async {
  final res = await http
      .get(Uri.parse('$_kPlantApiBase/notifications?plant_id=$plantId'))
      .timeout(const Duration(seconds: 15));
  return _parseOrThrow(
    res,
    (j) => (j as List<dynamic>)
        .map((e) => NotificationEvent.fromJson(e as Map<String, dynamic>))
        .toList(),
  );
}

const _kDefaultChatModel = 'exaone3.5:2.4b';

Future<String> sendPlantChatMessage(
  List<ChatMessage> history, {
  String model = _kDefaultChatModel,
}) async {
  final res = await http
      .post(
        Uri.parse('$_kPlantApiBase/chat'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'messages': history.map((m) => {'role': m.role, 'content': m.content}).toList(),
          'model': model,
        }),
      )
      .timeout(const Duration(seconds: 30));
  return _parseOrThrow(res, (j) => (j as Map<String, dynamic>)['text'] as String);
}
