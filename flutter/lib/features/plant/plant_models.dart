// fastapi/apps/plant 백엔드 응답과 1:1 대응하는 데이터 모델.
// 필드명은 www/lib/my-plants-api.ts, www/lib/plant-api.ts의 TS interface와 동일하게 맞춘다.

class ChatMessage {
  const ChatMessage({required this.role, required this.content});
  final String role;
  final String content;
}

class MyPlant {
  const MyPlant({
    required this.id,
    required this.nickname,
    required this.speciesName,
    required this.region,
    required this.growthStage,
    required this.points,
    required this.streakCount,
  });

  final int id;
  final String nickname;
  final String speciesName;
  final String region;
  final String growthStage;
  final int points;
  final int streakCount;

  factory MyPlant.fromJson(Map<String, dynamic> json) => MyPlant(
        id: json['id'] as int,
        nickname: json['nickname'] as String,
        speciesName: json['species_name'] as String,
        region: json['region'] as String,
        growthStage: json['growth_stage'] as String,
        points: json['points'] as int,
        streakCount: (json['streak_count'] as int?) ?? 0,
      );
}

class DiagnosisResult {
  const DiagnosisResult({
    required this.id,
    required this.plantId,
    required this.photoUrl,
    required this.detectedSpecies,
    required this.speciesConfidence,
    required this.symptomLabel,
    required this.symptomConfidence,
  });

  final int id;
  final int plantId;
  final String photoUrl;
  final String detectedSpecies;
  final double speciesConfidence;
  final String symptomLabel;
  final double symptomConfidence;

  factory DiagnosisResult.fromJson(Map<String, dynamic> json) => DiagnosisResult(
        id: json['id'] as int,
        plantId: json['plant_id'] as int,
        photoUrl: json['photo_url'] as String,
        detectedSpecies: json['detected_species'] as String,
        speciesConfidence: (json['species_confidence'] as num).toDouble(),
        symptomLabel: json['symptom_label'] as String,
        symptomConfidence: (json['symptom_confidence'] as num).toDouble(),
      );
}

class CareGuideResult {
  const CareGuideResult({
    required this.id,
    required this.diagnosisRecordId,
    required this.prescriptionText,
  });

  final int id;
  final int diagnosisRecordId;
  final String prescriptionText;

  factory CareGuideResult.fromJson(Map<String, dynamic> json) => CareGuideResult(
        id: json['id'] as int,
        diagnosisRecordId: json['diagnosis_record_id'] as int,
        prescriptionText: json['prescription_text'] as String,
      );
}

class CheckinResult {
  const CheckinResult({
    required this.id,
    required this.plantId,
    required this.checkinDate,
    required this.healthScore,
    required this.pointsEarned,
    required this.streakDay,
    required this.totalPoints,
    required this.growthStage,
    required this.newBadges,
  });

  final int id;
  final int plantId;
  final String checkinDate;
  final int healthScore;
  final int pointsEarned;
  final int streakDay;
  final int totalPoints;
  final String growthStage;
  final List<String> newBadges;

  factory CheckinResult.fromJson(Map<String, dynamic> json) => CheckinResult(
        id: json['id'] as int,
        plantId: json['plant_id'] as int,
        checkinDate: json['checkin_date'] as String,
        healthScore: json['health_score'] as int,
        pointsEarned: json['points_earned'] as int,
        streakDay: json['streak_day'] as int,
        totalPoints: json['total_points'] as int,
        growthStage: json['growth_stage'] as String,
        newBadges: (json['new_badges'] as List<dynamic>).map((e) => e as String).toList(),
      );
}

class CheckinHistoryItem {
  const CheckinHistoryItem({
    required this.id,
    required this.photoUrl,
    required this.checkinDate,
    required this.healthScore,
    required this.pointsEarned,
    required this.streakDay,
  });

  final int id;
  final String photoUrl;
  final String checkinDate;
  final int healthScore;
  final int pointsEarned;
  final int streakDay;

  factory CheckinHistoryItem.fromJson(Map<String, dynamic> json) => CheckinHistoryItem(
        id: json['id'] as int,
        photoUrl: json['photo_url'] as String,
        checkinDate: json['checkin_date'] as String,
        healthScore: json['health_score'] as int,
        pointsEarned: json['points_earned'] as int,
        streakDay: json['streak_day'] as int,
      );
}

class PlantBadge {
  const PlantBadge({
    required this.code,
    required this.name,
    required this.description,
    required this.icon,
    required this.earned,
    required this.earnedAt,
  });

  final String code;
  final String name;
  final String description;
  final String icon;
  final bool earned;
  final String? earnedAt;

  factory PlantBadge.fromJson(Map<String, dynamic> json) => PlantBadge(
        code: json['code'] as String,
        name: json['name'] as String,
        description: json['description'] as String,
        icon: json['icon'] as String,
        earned: json['earned'] as bool,
        earnedAt: json['earned_at'] as String?,
      );
}

class LeaderboardEntry {
  const LeaderboardEntry({
    required this.rank,
    required this.plantId,
    required this.nickname,
    required this.speciesName,
    required this.points,
    required this.growthStage,
  });

  final int rank;
  final int plantId;
  final String nickname;
  final String speciesName;
  final int points;
  final String growthStage;

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) => LeaderboardEntry(
        rank: json['rank'] as int,
        plantId: json['plant_id'] as int,
        nickname: json['nickname'] as String,
        speciesName: json['species_name'] as String,
        points: json['points'] as int,
        growthStage: json['growth_stage'] as String,
      );
}

class WeatherSnapshot {
  const WeatherSnapshot({
    required this.id,
    required this.region,
    required this.tempC,
    required this.humidityPct,
    required this.sunlightDesc,
    required this.isDryDay,
  });

  final int id;
  final String region;
  final double tempC;
  final double humidityPct;
  final String sunlightDesc;
  final bool isDryDay;

  factory WeatherSnapshot.fromJson(Map<String, dynamic> json) => WeatherSnapshot(
        id: json['id'] as int,
        region: json['region'] as String,
        tempC: (json['temp_c'] as num).toDouble(),
        humidityPct: (json['humidity_pct'] as num).toDouble(),
        sunlightDesc: json['sunlight_desc'] as String,
        isDryDay: json['is_dry_day'] as bool,
      );
}

class NotificationEvent {
  const NotificationEvent({
    required this.id,
    required this.plantId,
    required this.channel,
    required this.message,
    required this.coupangLink,
    required this.deliveryStatus,
  });

  final int id;
  final int? plantId;
  final String channel;
  final String message;
  final String? coupangLink;
  final String deliveryStatus;

  factory NotificationEvent.fromJson(Map<String, dynamic> json) => NotificationEvent(
        id: json['id'] as int,
        plantId: json['plant_id'] as int?,
        channel: json['channel'] as String,
        message: json['message'] as String,
        coupangLink: json['coupang_link'] as String?,
        deliveryStatus: json['delivery_status'] as String,
      );
}

