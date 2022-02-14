import json
import logging
import sys

import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig()
logger = logging.getLogger(__name__)


def calc_finishing(
        shooting_overall_goals,
        shooting_overall_shots_on_target,
        shooting_overall_shots_off_target
):
    # 決定力の基礎計算式
    # ゴール*9 - 枠内シュート*0.5 - 枠外シュート*3+1
    stats_item_finishing_buf = shooting_overall_goals * 9 \
                               - shooting_overall_shots_on_target * 0.5 \
                               - shooting_overall_shots_off_target * 3 \
                               + 1
    logger.debug(f'決定力要素 {stats_item_finishing_buf}')

    stats_item_finishing_linear_func_x = [-10, 6]  # 第1成績調整
    stats_item_finishing_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_finishing_linear_func_x2 = [1, 20]  # 第2成績調整
    stats_item_finishing_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_finishing_linear_func_x
    y = stats_item_finishing_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_finishing = 30 + slope * stats_item_finishing_buf + intercept
    # print(stats_item_finishing)

    if stats_item_finishing > 90:
        x = stats_item_finishing_linear_func_x2
    y = stats_item_finishing_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_finishing = stats_item_finishing - 90
    stats_item_finishing = slope * stats_item_finishing + intercept
    stats_item_finishing = stats_item_finishing + 90

    stats_item_finishing = round(stats_item_finishing)
    stats_item_finishing = np.clip(stats_item_finishing, 30, 99)
    logger.debug(f'決定力 {stats_item_finishing}')

    return int(stats_item_finishing)


def calc_att_positioning(
        shooting_overall_shots_on_target,
        defending_overall_air_duels_won
):
    # 攻撃_ポジショニングの基礎計算式
    # 枠内シュート数 +  空中戦勝利*1.5
    stats_item_att_positioning_buf = shooting_overall_shots_on_target \
                                     + defending_overall_air_duels_won * 1.5
    logger.debug(f'攻撃_ポジショニング要素 {stats_item_att_positioning_buf}')

    stats_item_att_positioning_linear_func_x = [0, 7]  # 第1成績調整
    stats_item_att_positioning_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_att_positioning_linear_func_x2 = [0, 20]  # 第2成績調整
    stats_item_att_positioning_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_att_positioning_linear_func_x
    y = stats_item_att_positioning_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_att_positioning = 30 + slope * stats_item_att_positioning_buf + intercept
    # print(stats_item_att_positioning)

    if stats_item_att_positioning > 90:
        x = stats_item_att_positioning_linear_func_x2
    y = stats_item_att_positioning_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_att_positioning = stats_item_att_positioning - 90
    stats_item_att_positioning = slope * stats_item_att_positioning + intercept
    stats_item_att_positioning = stats_item_att_positioning + 90

    stats_item_att_positioning = round(stats_item_att_positioning)
    stats_item_att_positioning = np.clip(stats_item_att_positioning, 30, 99)
    logger.debug(f'攻撃_ポジショニング {stats_item_att_positioning}')

    return int(stats_item_att_positioning)


def calc_shortpass(
        passing_types_ground,
        passing_types_through,
        passing_overall_intercepted,
        passing_overall_assists
):
    # ショートパスの基礎計算式
    # グラウンダーパス + スルーパス*1.2 - パス失敗*0.5 + アシスト*5
    stats_item_shortpass_buf = passing_types_ground + \
                               passing_types_through * 1.2 \
                               - passing_overall_intercepted * 0.5 \
                               + passing_overall_assists * 5
    logger.debug(f'ショートパス要素 {stats_item_shortpass_buf}')

    stats_item_shortpass_linear_func_x = [1, 30]  # 第1成績調整
    stats_item_shortpass_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_shortpass_linear_func_x2 = [1, 30]  # 第2成績調整
    stats_item_shortpass_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_shortpass_linear_func_x
    y = stats_item_shortpass_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_shortpass = 30 + slope * stats_item_shortpass_buf + intercept
    # print(stats_item_shortpass)

    if stats_item_shortpass > 90:
        x = stats_item_shortpass_linear_func_x2
    y = stats_item_shortpass_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_shortpass = stats_item_shortpass - 90
    stats_item_shortpass = slope * stats_item_shortpass + intercept
    stats_item_shortpass = stats_item_shortpass + 90

    stats_item_shortpass = round(stats_item_shortpass)
    stats_item_shortpass = np.clip(stats_item_shortpass, 30, 99)
    logger.debug(f'ショートパス {stats_item_shortpass}')

    return int(stats_item_shortpass)


def calc_longpass(
        passing_types_lob,
        passing_types_lofted_through,
        passing_overall_intercepted,
        passing_overall_assists,
        passing_types_set_pieces,
        passing_types_cross
):
    # ロングパスの基礎計算式
    # ロブパス + ロブスルーパス*1.2 - パス失敗*0.5 + アシスト*3 + セットプレーパス + クロス*1.5
    stats_item_longpass_buf = passing_types_lob \
                              + passing_types_lofted_through * 1.2 \
                              - passing_overall_intercepted * 0.5 \
                              + passing_overall_assists * 3 \
                              + passing_types_set_pieces \
                              + passing_types_cross * 1.5
    logger.debug(f'ロングパス要素 {stats_item_longpass_buf}')

    stats_item_longpass_linear_func_x = [1, 18]  # 第1成績調整
    stats_item_longpass_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_longpass_linear_func_x2 = [1, 18]  # 第2成績調整
    stats_item_longpass_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_longpass_linear_func_x
    y = stats_item_longpass_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_longpass = 30 + slope * stats_item_longpass_buf + intercept
    # print(stats_item_longpass)

    if stats_item_longpass > 90:
        x = stats_item_longpass_linear_func_x2
    y = stats_item_longpass_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_longpass = stats_item_longpass - 90
    stats_item_longpass = slope * stats_item_longpass + intercept
    stats_item_longpass = stats_item_longpass + 90

    stats_item_longpass = round(stats_item_longpass)
    stats_item_longpass = np.clip(stats_item_longpass, 30, 99)
    logger.debug(f'ロングパス {stats_item_longpass}')

    return int(stats_item_longpass)


def calc_vision(
        passing_overall_completed,
        passing_overall_passes,
        passing_overall_assists
):
    # 視野の基礎計算式
    # パス成功 / 総パス数 *10 ) - 12 + アシスト*2 + パス総数*0.5
    stats_item_vision_buf = -12 \
                            + passing_overall_assists * 3 \
                            + passing_overall_completed * 0.5
    if passing_overall_passes > 0:
        stats_item_vision_buf += passing_overall_completed / passing_overall_passes * 10
    logger.debug(f'視野要素 {stats_item_vision_buf}')

    stats_item_vision_linear_func_x = [0, 10]  # 第1成績調整
    stats_item_vision_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_vision_linear_func_x2 = [0, 15]  # 第2成績調整
    stats_item_vision_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_vision_linear_func_x
    y = stats_item_vision_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_vision = 30 + slope * stats_item_vision_buf + intercept
    # print(stats_item_vision)

    if stats_item_vision > 90:
        x = stats_item_vision_linear_func_x2
    y = stats_item_vision_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_vision = stats_item_vision - 90
    stats_item_vision = slope * stats_item_vision + intercept
    stats_item_vision = stats_item_vision + 90

    stats_item_vision = round(stats_item_vision)
    stats_item_vision = np.clip(stats_item_vision, 30, 99)
    logger.debug(f'視野 {stats_item_vision}')

    return int(stats_item_vision)


def calc_cross(
        passing_overall_expected_assists,
        passing_types_cross
):
    # クロスの基礎計算式
    # 予測アシスト + クロス成功数*0.7
    stats_item_cross_buf = passing_overall_expected_assists \
                           + passing_types_cross * 0.7
    logger.debug(f'クロス要素 {stats_item_cross_buf}')

    stats_item_cross_linear_func_x = [0, 2.5]  # 第1成績調整
    stats_item_cross_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_cross_linear_func_x2 = [0, 23]  # 第2成績調整
    stats_item_cross_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_cross_linear_func_x
    y = stats_item_cross_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_cross = 30 + slope * stats_item_cross_buf + intercept
    # print(stats_item_cross)

    if stats_item_cross > 90:
        x = stats_item_cross_linear_func_x2
    y = stats_item_cross_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_cross = stats_item_cross - 90
    stats_item_cross = slope * stats_item_cross + intercept
    stats_item_cross = stats_item_cross + 90

    stats_item_cross = round(stats_item_cross)
    stats_item_cross = np.clip(stats_item_cross, 30, 99)
    logger.debug(f'クロス {stats_item_cross}')

    return int(stats_item_cross)


def calc_agility(
        summary_distance_sprinted,
        possession_overall_regular_dribble,
        possession_overall_strafe_dribble,
        possession_overall_shield_dribble,
        possession_types_knock_ons,
        possession_types_skillmove_beat,
        possession_types_nutmeg
):
    # 敏捷値の基礎計算式
    # スプリント/3 + 通常ドリブル/90 + ストレイフ/2 + シールドドリ /2 + ノックオン*0.7 + スキム突破 + ナツメグ*3
    stats_item_agility_buf = summary_distance_sprinted / 3 \
                             + possession_overall_regular_dribble / 90 \
                             + possession_overall_strafe_dribble / 2 \
                             + possession_overall_shield_dribble / 2 \
                             + possession_types_knock_ons * 0.7 \
                             + possession_types_skillmove_beat \
                             + possession_types_nutmeg * 3
    logger.debug(f'敏捷値要素 {stats_item_agility_buf}')

    stats_item_agility_linear_func_x = [0, 15]  # 第1成績調整
    stats_item_agility_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_agility_linear_func_x2 = [0, 25]  # 第2成績調整
    stats_item_agility_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_agility_linear_func_x
    y = stats_item_agility_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_agility = 30 + slope * stats_item_agility_buf + intercept
    # print(stats_item_agility)

    if stats_item_agility > 90:
        x = stats_item_agility_linear_func_x2
    y = stats_item_agility_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_agility = stats_item_agility - 90
    stats_item_agility = slope * stats_item_agility + intercept
    stats_item_agility = stats_item_agility + 90

    stats_item_agility = round(stats_item_agility)
    stats_item_agility = np.clip(stats_item_agility, 30, 99)
    logger.debug(f'敏捷値 {stats_item_agility}')

    return int(stats_item_agility)


def calc_ball_control(
        possession_overall_possession,
        possession_overall_dribbles_completed,
        possession_overall_dribbles
):
    # ボールコントロールの基礎計算式
    # ポゼッション + ドリブル成功率*10
    stats_item_ball_controll_buf = possession_overall_possession
    if possession_overall_dribbles > 0:
        stats_item_ball_controll_buf += possession_overall_dribbles_completed / possession_overall_dribbles * 10
    logger.debug(f'ボールコントロール要素 {stats_item_ball_controll_buf}')

    stats_item_ball_controll_linear_func_x = [0, 15]  # 第1成績調整
    stats_item_ball_controll_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_ball_controll_linear_func_x2 = [0, 25]  # 第2成績調整
    stats_item_ball_controll_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_ball_controll_linear_func_x
    y = stats_item_ball_controll_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_ball_controll = 30 + slope * stats_item_ball_controll_buf + intercept
    # print(stats_item_ball_controll)

    if stats_item_ball_controll > 90:
        x = stats_item_ball_controll_linear_func_x2
    y = stats_item_ball_controll_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_ball_controll = stats_item_ball_controll - 90
    stats_item_ball_controll = slope * stats_item_ball_controll + intercept
    stats_item_ball_controll = stats_item_ball_controll + 90

    stats_item_ball_controll = round(stats_item_ball_controll)
    stats_item_ball_controll = np.clip(stats_item_ball_controll, 30, 99)
    logger.debug(f'ボールコントロール {stats_item_ball_controll}')

    return int(stats_item_ball_controll)


def calc_dribble(
        possession_overall_regular_dribble,
        possession_overall_strafe_dribble,
        possession_overall_shield_dribble,
        possession_types_knock_ons,
        possession_types_skillmove_beat,
        possession_types_nutmeg,
        possession_overall_distance_dribbled,
        possession_overall_dribbles_completed,
        possession_overall_dribbles,
):
    # ドリブルの基礎計算式
    # 通常ドリブル/90 + ストレイフ/2 + シールドドリ /2 + ノックオン*0.7 + スキム突破 + ナツメグ*3 + ドリブル距離*1.5 + ドリブル成功率*10
    stats_item_dribless_buf = possession_overall_regular_dribble / 90 \
                              + possession_overall_strafe_dribble / 2 \
                              + possession_overall_shield_dribble / 2 \
                              + possession_types_knock_ons * 0.7 \
                              + possession_types_skillmove_beat \
                              + possession_types_nutmeg * 3 \
                              + possession_overall_distance_dribbled * 1.5
    if possession_overall_dribbles > 0:
        possession_overall_dribbles += possession_overall_dribbles_completed / possession_overall_dribbles * 10
    logger.debug(f'ドリブル要素 {stats_item_dribless_buf}')

    stats_item_dribless_linear_func_x = [0, 20]  # 第1成績調整
    stats_item_dribless_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_dribless_linear_func_x2 = [0, 30]  # 第2成績調整
    stats_item_dribless_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_dribless_linear_func_x
    y = stats_item_dribless_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_dribless = 30 + slope * stats_item_dribless_buf + intercept
    # print(stats_item_dribless)

    if stats_item_dribless > 90:
        x = stats_item_dribless_linear_func_x2
    y = stats_item_dribless_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_dribless = stats_item_dribless - 90
    stats_item_dribless = slope * stats_item_dribless + intercept
    stats_item_dribless = stats_item_dribless + 90

    stats_item_dribless = round(stats_item_dribless)
    stats_item_dribless = np.clip(stats_item_dribless, 30, 99)
    logger.debug(f'ドリブル {stats_item_dribless}')

    return int(stats_item_dribless)


def calc_composure(
        shooting_overall_shots_on_target,
        shooting_overall_shots,
        possession_overall_dribbles_completed,
        possession_overall_dribbles,
        defending_overall_sliding_tackles_won,
        defending_overall_sliding_tackles,
        defending_overall_standing_tackles_won,
        defending_overall_standing_tackles,
        shooting_types_low,
        shooting_types_chip,
):
    # 冷静さの基礎計算式
    # シュート枠内例効率*3+ドリブル成功率*2+各タックル成功率*2+低弾道シュート*2+チップシュート*3
    stats_item_composure_buf = shooting_types_low * 2 \
                               + shooting_types_chip * 3
    if shooting_overall_shots > 0:
        stats_item_composure_buf += shooting_overall_shots_on_target / shooting_overall_shots * 3
    if possession_overall_dribbles > 0:
        stats_item_composure_buf += possession_overall_dribbles_completed / possession_overall_dribbles * 2
    if defending_overall_sliding_tackles > 0:
        stats_item_composure_buf += defending_overall_sliding_tackles_won / defending_overall_sliding_tackles * 2
    if defending_overall_standing_tackles > 0:
        stats_item_composure_buf += defending_overall_standing_tackles_won / defending_overall_standing_tackles * 2
    logger.debug(f'冷静さ要素 {stats_item_composure_buf}')

    stats_item_composure_linear_func_x = [0, 7.0]  # 第1成績調整
    stats_item_composure_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_composure_linear_func_x2 = [0, 30]  # 第2成績調整
    stats_item_composure_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_composure_linear_func_x
    y = stats_item_composure_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_composure = 30 + slope * stats_item_composure_buf + intercept
    # print(stats_item_composure)

    if stats_item_composure > 90:
        x = stats_item_composure_linear_func_x2
    y = stats_item_composure_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_composure = stats_item_composure - 90
    stats_item_composure = slope * stats_item_composure + intercept
    stats_item_composure = stats_item_composure + 90

    stats_item_composure = round(stats_item_composure)
    stats_item_composure = np.clip(stats_item_composure, 30, 99)
    logger.debug(f'冷静さ {stats_item_composure}')

    return int(stats_item_composure)


def calc_interceptions(defending_overall_interceptions):
    # インターセプトの基礎計算式
    # インターセプト
    stats_item_interceptions_buf = defending_overall_interceptions
    logger.debug(f'インターセプト要素 {stats_item_interceptions_buf}')

    stats_item_interceptions_linear_func_x = [0, 3]  # 第1成績調整
    stats_item_interceptions_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_interceptions_linear_func_x2 = [0, 50]  # 第2成績調整
    stats_item_interceptions_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_interceptions_linear_func_x
    y = stats_item_interceptions_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_interceptions = 30 + slope * stats_item_interceptions_buf + intercept
    # print(stats_item_interceptions)

    if stats_item_interceptions > 90:
        x = stats_item_interceptions_linear_func_x2
    y = stats_item_interceptions_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_interceptions = stats_item_interceptions - 90
    stats_item_interceptions = slope * stats_item_interceptions + intercept
    stats_item_interceptions = stats_item_interceptions + 90

    stats_item_interceptions = round(stats_item_interceptions)
    stats_item_interceptions = np.clip(stats_item_interceptions, 30, 99)
    logger.debug(f'インターセプト {stats_item_interceptions}')

    return int(stats_item_interceptions)


def calc_awareness(
        defending_overall_sliding_tackles_won,
        defending_overall_sliding_tackles,
        defending_overall_standing_tackles_won,
        defending_overall_standing_tackles,
        defending_overall_air_duels_won,
        defending_overall_beaten_by_opponent,
):
    # マークの基礎計算式
    # 各タックル成功率 + 空中勝利*1.2　- 抜かれた回数*1.4
    stats_item_awareness_buf = defending_overall_air_duels_won * 1.2 \
                               - defending_overall_beaten_by_opponent * 1.4
    if defending_overall_sliding_tackles > 0:
        stats_item_awareness_buf += defending_overall_sliding_tackles_won / defending_overall_sliding_tackles * 2
    if defending_overall_standing_tackles > 0:
        stats_item_awareness_buf += defending_overall_standing_tackles_won / defending_overall_standing_tackles * 2
    logger.debug(f'マーク要素 {stats_item_awareness_buf}')

    stats_item_awareness_linear_func_x = [0, 5]  # 第1成績調整
    stats_item_awareness_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_awareness_linear_func_x2 = [0, 10]  # 第2成績調整
    stats_item_awareness_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_awareness_linear_func_x
    y = stats_item_awareness_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_awareness = 30 + slope * stats_item_awareness_buf + intercept
    # print(stats_item_awareness)

    if stats_item_awareness > 90:
        x = stats_item_awareness_linear_func_x2
    y = stats_item_awareness_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_awareness = stats_item_awareness - 90
    stats_item_awareness = slope * stats_item_awareness + intercept
    stats_item_awareness = stats_item_awareness + 90

    stats_item_awareness = round(stats_item_awareness)
    stats_item_awareness = np.clip(stats_item_awareness, 30, 99)
    logger.debug(f'マーク {stats_item_awareness}')

    return int(stats_item_awareness)


def calc_standing_tackles(
        defending_overall_standing_tackles_won,
        defending_overall_standing_tackles,
):
    # スタンディングタックルの基礎計算式
    # タックル成功率 + タックル数*1.5
    stats_item_standing_tackle_buf = defending_overall_standing_tackles_won * 1.3
    if defending_overall_standing_tackles > 0:
        stats_item_standing_tackle_buf += defending_overall_standing_tackles_won / defending_overall_standing_tackles * 5
    logger.debug(f'スタンディングタックル要素 {stats_item_standing_tackle_buf}')

    stats_item_standing_tackle_linear_func_x = [0, 7]  # 第1成績調整
    stats_item_standing_tackle_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_standing_tackle_linear_func_x2 = [0, 20]  # 第2成績調整
    stats_item_standing_tackle_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_standing_tackle_linear_func_x
    y = stats_item_standing_tackle_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_standing_tackle = 30 + slope * stats_item_standing_tackle_buf + intercept
    # print(stats_item_standing_tackle)

    if stats_item_standing_tackle > 90:
        x = stats_item_standing_tackle_linear_func_x2
    y = stats_item_standing_tackle_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_standing_tackle = stats_item_standing_tackle - 90
    stats_item_standing_tackle = slope * stats_item_standing_tackle + intercept
    stats_item_standing_tackle = stats_item_standing_tackle + 90

    stats_item_standing_tackle = round(stats_item_standing_tackle)
    stats_item_standing_tackle = np.clip(stats_item_standing_tackle, 30, 99)
    logger.debug(f'スタンディングタックル {stats_item_standing_tackle}')

    return int(stats_item_standing_tackle)


def calc_sliding_tackles(
        defending_overall_sliding_tackles_won,
        defending_overall_sliding_tackles,
):
    # スライディングタックルの基礎計算式
    # タックル成功率 + タックル数*1.5
    stats_item_sliding_tackle_buf = defending_overall_sliding_tackles_won * 1.3
    if defending_overall_sliding_tackles > 0:
        stats_item_sliding_tackle_buf += defending_overall_sliding_tackles_won / defending_overall_sliding_tackles * 5
    logger.debug(f'スライディングタックル要素 {stats_item_sliding_tackle_buf}')

    stats_item_sliding_tackle_linear_func_x = [0, 7]  # 第1成績調整
    stats_item_sliding_tackle_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_sliding_tackle_linear_func_x2 = [0, 20]  # 第2成績調整
    stats_item_sliding_tackle_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_sliding_tackle_linear_func_x
    y = stats_item_sliding_tackle_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_sliding_tackle = 30 + slope * stats_item_sliding_tackle_buf + intercept
    # print(stats_item_sliding_tackle)

    if stats_item_sliding_tackle > 90:
        x = stats_item_sliding_tackle_linear_func_x2
    y = stats_item_sliding_tackle_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_sliding_tackle = stats_item_sliding_tackle - 90
    stats_item_sliding_tackle = slope * stats_item_sliding_tackle + intercept
    stats_item_sliding_tackle = stats_item_sliding_tackle + 90

    stats_item_sliding_tackle = round(stats_item_sliding_tackle)
    stats_item_sliding_tackle = np.clip(stats_item_sliding_tackle, 30, 99)
    logger.debug(f'スライディングタックル {stats_item_sliding_tackle}')

    return int(stats_item_sliding_tackle)


def calc_jump(
        defending_overall_air_duels_won
):
    # ジャンプの基礎計算式
    # 空中戦勝利
    stats_item_jump_buf = defending_overall_air_duels_won
    logger.debug(f'ジャンプ要素 {stats_item_jump_buf}')

    stats_item_jump_linear_func_x = [0, 3]  # 第1成績調整
    stats_item_jump_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_jump_linear_func_x2 = [0, 50]  # 第2成績調整
    stats_item_jump_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_jump_linear_func_x
    y = stats_item_jump_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_jump = 30 + slope * stats_item_jump_buf + intercept
    # print(stats_item_jump)

    if stats_item_jump > 90:
        x = stats_item_jump_linear_func_x2
    y = stats_item_jump_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_jump = stats_item_jump - 90
    stats_item_jump = slope * stats_item_jump + intercept
    stats_item_jump = stats_item_jump + 90

    stats_item_jump = round(stats_item_jump)
    stats_item_jump = np.clip(stats_item_jump, 30, 99)
    logger.debug(f'ジャンプ {stats_item_jump}')

    return int(stats_item_jump)


def calc_stamina(
        summary_distance_covered
):
    # スタミナの基礎計算式
    # 移動距離
    stats_item_stamina_buf = summary_distance_covered
    logger.debug(f'スタミナ要素 {stats_item_stamina_buf}')

    stats_item_stamina_linear_func_x = [0, 10]  # 第1成績調整
    stats_item_stamina_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_stamina_linear_func_x2 = [0, 32]  # 第2成績調整
    stats_item_stamina_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_stamina_linear_func_x
    y = stats_item_stamina_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_stamina = 30 + slope * stats_item_stamina_buf + intercept
    # print(stats_item_stamina)

    if stats_item_stamina > 90:
        x = stats_item_stamina_linear_func_x2
    y = stats_item_stamina_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_stamina = stats_item_stamina - 90
    stats_item_stamina = slope * stats_item_stamina + intercept
    stats_item_stamina = stats_item_stamina + 90

    stats_item_stamina = round(stats_item_stamina)
    stats_item_stamina = np.clip(stats_item_stamina, 30, 99)
    logger.debug(f'スタミナ {stats_item_stamina}')

    return int(stats_item_stamina)


def calc_strength(
        defending_overall_sliding_tackles_won,
        defending_overall_sliding_tackles,
        defending_overall_standing_tackles_won,
        defending_overall_standing_tackles,
        defending_overall_air_duels_won,
        defending_overall_beaten_by_opponent,
        defending_overall_blocks,
        defending_overall_clearance,
):
    # 強さの基礎計算式
    # 各タックル成功率 + 空中勝利*1.2　- 抜かれた回数*1.4 + ブロック数 + クリア数
    stats_item_strength_buf = defending_overall_air_duels_won * 1.2 \
                              - defending_overall_beaten_by_opponent * 1.4 \
                              + defending_overall_blocks \
                              + defending_overall_clearance
    if defending_overall_sliding_tackles > 0:
        stats_item_strength_buf += defending_overall_sliding_tackles_won / defending_overall_sliding_tackles * 2
    if defending_overall_standing_tackles > 0:
        stats_item_strength_buf += defending_overall_standing_tackles_won / defending_overall_standing_tackles * 2
    logger.debug(f'強さ要素 {stats_item_strength_buf}')

    stats_item_strength_linear_func_x = [0, 12]  # 第1成績調整
    stats_item_strength_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_strength_linear_func_x2 = [0, 30]  # 第2成績調整
    stats_item_strength_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_strength_linear_func_x
    y = stats_item_strength_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_strength = 30 + slope * stats_item_strength_buf + intercept
    # print(stats_item_strength)

    if stats_item_strength > 90:
        x = stats_item_strength_linear_func_x2
    y = stats_item_strength_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_strength = stats_item_strength - 90
    stats_item_strength = slope * stats_item_strength + intercept
    stats_item_strength = stats_item_strength + 90

    stats_item_strength = round(stats_item_strength)
    stats_item_strength = np.clip(stats_item_strength, 30, 99)
    logger.debug(f'強さ {stats_item_strength}')

    return int(stats_item_strength)


def calc_aggression(
        possession_overall_dribbles_completed,
        defending_overall_sliding_tackles_won,
        defending_overall_standing_tackles_won,
        defending_overall_interceptions,
        defending_overall_penalties_won,
        defending_overall_air_duels_won,
        defending_overall_blocks,
):
    # 積極性の基礎計算式
    # ドリブル勝利数 + 各タックル成功数　+ インターセプト*3 + PK獲得*4 + 空中戦勝利*2 + ブロック*2
    stats_item_aggression_buf = possession_overall_dribbles_completed \
                                + defending_overall_sliding_tackles_won \
                                + defending_overall_standing_tackles_won \
                                + defending_overall_interceptions * 3 \
                                + defending_overall_penalties_won * 4 \
                                + defending_overall_air_duels_won * 2 \
                                + defending_overall_blocks * 2
    logger.debug(f'積極性要素 {stats_item_aggression_buf}')

    stats_item_aggression_linear_func_x = [0, 60]  # 第1成績調整
    stats_item_aggression_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_aggression_linear_func_x2 = [0, 120]  # 第2成績調整
    stats_item_aggression_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_aggression_linear_func_x
    y = stats_item_aggression_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_aggression = 30 + slope * stats_item_aggression_buf + intercept
    # print(stats_item_aggression)

    if stats_item_aggression > 90:
        x = stats_item_aggression_linear_func_x2
    y = stats_item_aggression_linear_func_y2
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_aggression = stats_item_aggression - 90
    stats_item_aggression = slope * stats_item_aggression + intercept
    stats_item_aggression = stats_item_aggression + 90

    stats_item_aggression = round(stats_item_aggression)
    stats_item_aggression = np.clip(stats_item_aggression, 30, 99)
    logger.debug(f'積極性 {stats_item_aggression}')

    return int(stats_item_aggression)


def get_player_attr(player_stats_info: dict) -> dict:
    stats = player_stats_info['stats']
    result = {
        'finishing': calc_finishing(
            stats['shooting']['overall'].get('goals', 0),
            stats['shooting']['overall'].get('shots_on_target', 0),
            stats['shooting']['overall'].get('shots_off_target', 0),
        ),
        'att_positioning': calc_att_positioning(
            stats['shooting']['overall'].get('shots_on_target', 0),
            stats['defending']['overall'].get('air_duels_won', 0)
        ),
        'short_passing': calc_shortpass(
            stats['passing']['types'].get('ground', 0),
            stats['passing']['types'].get('through', 0),
            stats['passing']['overall'].get('intercepted', 0),
            stats['passing']['overall'].get('assists', 0)
        ),
        'long_passing': calc_longpass(
            stats['passing']['types'].get('lob', 0),
            stats['passing']['types'].get('lofted_through', 0),
            stats['passing']['overall'].get('intercepted', 0),
            stats['passing']['overall'].get('assists', 0),
            stats['passing']['types'].get('set_pieces', 0),
            stats['passing']['types'].get('cross', 0)
        ),
        'vision': calc_vision(
            stats['passing']['overall'].get('completed', 0),
            stats['passing']['overall'].get('passes', 0),
            stats['passing']['overall'].get('assists', 0)
        ),
        'crossing': calc_cross(
            stats['passing']['overall'].get('expected_assists', 0),
            stats['passing']['types'].get('cross', 0)
        ),
        'agility': calc_agility(
            stats['summary'].get('distance_sprinted', 0),
            stats['possession']['overall'].get('regular_dribble', 0),
            stats['possession']['overall'].get('strafe_dribble', 0),
            stats['possession']['overall'].get('shield_dribble', 0),
            stats['possession']['types'].get('knock_ons', 0),
            stats['possession']['types'].get('skillmove_beat', 0),
            stats['possession']['types'].get('nutmeg', 0)
        ),
        'ball_control': calc_ball_control(
            stats['possession']['overall'].get('possession', 0),
            stats['possession']['overall'].get('dribbles_completed', 0),
            stats['possession']['overall'].get('dribbles', 0)
        ),
        'dribbling': calc_dribble(
            stats['possession']['overall'].get('regular_dribble', 0),
            stats['possession']['overall'].get('strafe_dribble', 0),
            stats['possession']['overall'].get('shield_dribble', 0),
            stats['possession']['types'].get('knock_ons', 0),
            stats['possession']['types'].get('skillmove_beat', 0),
            stats['possession']['types'].get('nutmeg', 0),
            stats['possession']['overall'].get('distance_dribbled', 0),
            stats['possession']['overall'].get('dribbles_completed', 0),
            stats['possession']['overall'].get('dribbles', 0)
        ),
        'composure': calc_composure(
            stats['shooting']['overall'].get('shots_on_target', 0),
            stats['shooting']['overall'].get('shots', 0),
            stats['possession']['overall'].get('dribbles_completed', 0),
            stats['possession']['overall'].get('dribbles', 0),
            stats['defending']['overall'].get('sliding_tackles_won', 0),
            stats['defending']['overall'].get('sliding_tackles', 0),
            stats['defending']['overall'].get('standing_tackles_won', 0),
            stats['defending']['overall'].get('standing_tackles', 0),
            stats['shooting']['types'].get('low', 0),
            stats['shooting']['types'].get('chip', 0)
        ),
        'interceptions': calc_interceptions(
            stats['defending']['overall'].get('interceptions', 0)
        ),
        'awareness': calc_awareness(
            stats['defending']['overall'].get('sliding_tackles_won', 0),
            stats['defending']['overall'].get('sliding_tackles', 0),
            stats['defending']['overall'].get('standing_tackles_won', 0),
            stats['defending']['overall'].get('standing_tackles', 0),
            stats['defending']['overall'].get('air_duels_won', 0),
            stats['defending']['overall'].get('beaten_by_opponent', 0)
        ),
        'standing_tackle': calc_standing_tackles(
            stats['defending']['overall'].get('standing_tackles_won', 0),
            stats['defending']['overall'].get('standing_tackles', 0)
        ),
        'sliding_tackle': calc_sliding_tackles(
            stats['defending']['overall'].get('sliding_tackles_won', 0),
            stats['defending']['overall'].get('sliding_tackles', 0)
        ),
        'jump': calc_jump(
            stats['defending']['overall'].get('air_duels_won', 0)
        ),
        'stamina': calc_stamina(
            stats['summary'].get('distance_covered', 0)
        ),
        'strength': calc_strength(
            stats['defending']['overall'].get('sliding_tackles_won', 0),
            stats['defending']['overall'].get('sliding_tackles', 0),
            stats['defending']['overall'].get('standing_tackles_won', 0),
            stats['defending']['overall'].get('standing_tackles', 0),
            stats['defending']['overall'].get('air_duels_won', 0),
            stats['defending']['overall'].get('beaten_by_opponent', 0),
            stats['defending']['overall'].get('blocks', 0),
            stats['defending']['overall'].get('clearance', 0)
        ),
        'aggression': calc_aggression(
            stats['possession']['overall'].get('dribbles_completed', 0),
            stats['defending']['overall'].get('sliding_tackles_won', 0),
            stats['defending']['overall'].get('standing_tackles_won', 0),
            stats['defending']['overall'].get('interceptions', 0),
            stats['possession']['overall'].get('penalties_won', 0),
            stats['defending']['overall'].get('air_duels_won', 0),
            stats['defending']['overall'].get('blocks', 0)
        )
    }

    return result


def main():
    logger.setLevel(logging.INFO)
    with open(sys.argv[1], 'r') as fp:
        player_stats_info_list = [player_stats_info for player_stats_info in json.load(fp) if player_stats_info['position_type'] == sys.argv[3]]
        player_attr_list = [get_player_attr(player_stats_info) for player_stats_info in player_stats_info_list]
        logger.debug(json.dumps(player_attr_list, indent=2))
    plt.hist([player_attr[sys.argv[2]] for player_attr in player_attr_list], range=[30, 99], bins=69)
    plt.show()


if __name__ == '__main__':
    main()
