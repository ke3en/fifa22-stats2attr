# -*- coding: utf-8 -*-

import json
import logging
import sys

import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig()
logger = logging.getLogger(__name__)

# (0, 0), (50, 80), (100, 99)の3点を通る二次関数の係数
a = np.polyfit(x=[0, 50, 100], y=[0, 80, 99], deg=2)


def calc(x):
    x_clip = np.clip(x, 0, 100)
    y = a[0] * x_clip * x_clip + a[1] * x_clip + a[2]
    return np.clip(round(y), 0, 99)


def calc_finishing(stats):
    # 決定力
    # 決定機で確実にゴールを決める能力。
    # ゴール*50 + 枠内シュート*5 + 枠外シュート*(-15)
    x = stats['shooting']['overall'].get('goals', 0) * 50 \
        + stats['shooting']['overall'].get('shots_on_target', 0) * 5 \
        + stats['shooting']['overall'].get('shots_off_target', 0) * (-15)
    return calc(x)


def calc_att_positioning(stats):
    # 攻撃ポジショニング
    # ゴール前でボールを受けて決定機を作るオフザボールの能力。
    # ゴール期待値*30 + シュート*5 + 枠内シュート*5
    x = stats['shooting']['overall'].get('expected_goals', 0) * 30 \
        + stats['shooting']['overall'].get('shots', 0) * 5 \
        + stats['shooting']['overall'].get('shots_on_target', 0) * 5
    return calc(x)


def calc_passing(stats):
    # パス
    # パスを正確さ。
    # 30 + (パス成功率-0.7)/0.3*20 + パス成功
    x = 30 + (stats['passing']['overall'].get('completed', 0) / stats['passing']['overall'].get('passes', 1) - 0.7) / 0.3 * 20 \
        + stats['passing']['overall'].get('completed', 0)
    return calc(x)


def calc_vision(stats):
    # 視野
    # 敵味方の位置を把握し、決定機に繋がるパスをする能力。
    # アシスト期待値*30 + アシスト期待値*30 - 被インターセプト - 被オフサイド
    x = stats['passing']['overall'].get('assists', 0) * 30 \
        + stats['passing']['overall'].get('expected_assists', 0) * 30 \
        + (stats['passing']['types'].get('through', 0) + stats['passing']['types'].get('lofted_through', 0)) * (stats['passing']['overall'].get('completed', 0) / stats['passing']['overall'].get('passes', 1)) * 5 \
        + stats['passing']['overall'].get('intercepted', 0) * (-5) \
        + stats['passing']['overall'].get('offside_passes', 0) * (-3)
    return calc(x)


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
    stats_item_agility_linear_func_x2 = [0, 35]  # 第2成績調整
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
    stats_item_ball_control_buf = possession_overall_possession
    if possession_overall_dribbles > 0:
        stats_item_ball_control_buf += possession_overall_dribbles_completed / possession_overall_dribbles * 10
    logger.debug(f'ボールコントロール要素 {stats_item_ball_control_buf}')

    stats_item_ball_control_linear_func_x = [0, 15]  # 第1成績調整
    stats_item_ball_control_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_ball_control_linear_func_x2 = [0, 23]  # 第2成績調整
    stats_item_ball_control_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_ball_control_linear_func_x
    y = stats_item_ball_control_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_ball_control = 30 + slope * stats_item_ball_control_buf + intercept
    # print(stats_item_ball_control)

    if stats_item_ball_control > 90:
        x = stats_item_ball_control_linear_func_x2
        y = stats_item_ball_control_linear_func_y2
        slope, intercept = np.polyfit(x, y, 1)
        stats_item_ball_control = stats_item_ball_control - 90
        stats_item_ball_control = slope * stats_item_ball_control + intercept
        stats_item_ball_control = stats_item_ball_control + 90

    stats_item_ball_control = round(stats_item_ball_control)
    stats_item_ball_control = np.clip(stats_item_ball_control, 30, 99)
    logger.debug(f'ボールコントロール {stats_item_ball_control}')

    return int(stats_item_ball_control)


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
    stats_item_dribbles_buf = possession_overall_regular_dribble / 90 \
                              + possession_overall_strafe_dribble / 2 \
                              + possession_overall_shield_dribble / 2 \
                              + possession_types_knock_ons * 0.7 \
                              + possession_types_skillmove_beat \
                              + possession_types_nutmeg * 3 \
                              + possession_overall_distance_dribbled * 1.5
    if possession_overall_dribbles > 0:
        possession_overall_dribbles += possession_overall_dribbles_completed / possession_overall_dribbles * 10
    logger.debug(f'ドリブル要素 {stats_item_dribbles_buf}')

    stats_item_dribbles_linear_func_x = [0, 14]  # 第1成績調整
    stats_item_dribbles_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_dribbles_linear_func_x2 = [0, 36]  # 第2成績調整
    stats_item_dribbles_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_dribbles_linear_func_x
    y = stats_item_dribbles_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_dribbles = 30 + slope * stats_item_dribbles_buf + intercept
    # print(stats_item_dribbles)

    if stats_item_dribbles > 90:
        x = stats_item_dribbles_linear_func_x2
        y = stats_item_dribbles_linear_func_y2
        slope, intercept = np.polyfit(x, y, 1)
        stats_item_dribbles = stats_item_dribbles - 90
        stats_item_dribbles = slope * stats_item_dribbles + intercept
        stats_item_dribbles = stats_item_dribbles + 90

    stats_item_dribbles = round(stats_item_dribbles)
    stats_item_dribbles = np.clip(stats_item_dribbles, 30, 99)
    logger.debug(f'ドリブル {stats_item_dribbles}')

    return int(stats_item_dribbles)


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


def calc_interceptions(
        defending_overall_interceptions
):
    # インターセプトの基礎計算式
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
    # 各タックル成功率*2.6 + 空中勝利*1.2　- 抜かれた回数*1.4
    stats_item_awareness_buf = defending_overall_air_duels_won * 1.2 \
                               - defending_overall_beaten_by_opponent * 1.4
    if defending_overall_sliding_tackles > 0:
        stats_item_awareness_buf += defending_overall_sliding_tackles_won / defending_overall_sliding_tackles * 3
    if defending_overall_standing_tackles > 0:
        stats_item_awareness_buf += defending_overall_standing_tackles_won / defending_overall_standing_tackles * 3
    logger.debug(f'マーク要素 {stats_item_awareness_buf}')

    stats_item_awareness_linear_func_x = [0, 4.8]  # 第1成績調整
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
    # タックル成功率*2 + タックル数*2
    stats_item_standing_tackle_buf = defending_overall_standing_tackles_won * 2
    if defending_overall_standing_tackles > 0:
        stats_item_standing_tackle_buf += defending_overall_standing_tackles_won / defending_overall_standing_tackles * 2
    logger.debug(f'スタンディングタックル要素 {stats_item_standing_tackle_buf}')

    stats_item_standing_tackle_linear_func_x = [0, 7.5]  # 第1成績調整
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
    stats_item_stamina_linear_func_x2 = [0, 40]  # 第2成績調整
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
        shooting_overall_shots_on_target,
        shooting_overall_shots,
        possession_overall_dribbles_completed,
        possession_overall_dribbles

):
    # 強さの基礎計算式　　下記いずれか高い方
    # 守備系　各タックル成功率*3 + 空中勝利*1.5　- 抜かれた回数*1.4 + ブロック数 + クリア数
    # 攻撃系　各タックル成功率*3 + 空中勝利*1.5 + シュート枠内率*3 + ドリブル成功率*3

    # 守備 BUF
    stats_item_strength_buf = defending_overall_air_duels_won * 1.5 \
                              - defending_overall_beaten_by_opponent * 1.4 \
                              + defending_overall_blocks \
                              + defending_overall_clearance
    if defending_overall_sliding_tackles > 0:
        stats_item_strength_buf += defending_overall_sliding_tackles_won / defending_overall_sliding_tackles * 3
    if defending_overall_standing_tackles > 0:
        stats_item_strength_buf += defending_overall_standing_tackles_won / defending_overall_standing_tackles * 3
    logger.debug(f'強さ要素 {stats_item_strength_buf}')

    stats_item_strength_buf1 = defending_overall_air_duels_won * 1.5 \
 \
        # 攻撃 BUF1
    if defending_overall_sliding_tackles > 0:
        stats_item_strength_buf1 += defending_overall_sliding_tackles_won / defending_overall_sliding_tackles * 3
    if defending_overall_standing_tackles > 0:
        stats_item_strength_buf1 += defending_overall_standing_tackles_won / defending_overall_standing_tackles * 3
    if shooting_overall_shots > 0:
        stats_item_strength_buf1 += shooting_overall_shots_on_target / shooting_overall_shots * 3
    if possession_overall_dribbles > 0:
        stats_item_strength_buf1 += possession_overall_dribbles_completed / possession_overall_dribbles * 3

    if stats_item_strength_buf1 > stats_item_strength_buf:
        stats_item_strength_buf2 = stats_item_strength_buf1
    else:
        stats_item_strength_buf2 = stats_item_strength_buf

    stats_item_strength_linear_func_x = [0, 9]  # 第1成績調整
    stats_item_strength_linear_func_y = [30, 60]  # 第1可変レンジ
    stats_item_strength_linear_func_x2 = [0, 30]  # 第2成績調整
    stats_item_strength_linear_func_y2 = [0, 10]  # 第2可変レンジ 90～99用

    x = stats_item_strength_linear_func_x
    y = stats_item_strength_linear_func_y
    slope, intercept = np.polyfit(x, y, 1)
    stats_item_strength = 30 + slope * stats_item_strength_buf2 + intercept
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
    # ドリブル勝利数 + 各タックル成功数　+ インターセプト*10 + PK獲得*4 + 空中戦勝利*2 + ブロック*2
    stats_item_aggression_buf = possession_overall_dribbles_completed \
                                + defending_overall_sliding_tackles_won \
                                + defending_overall_standing_tackles_won \
                                + defending_overall_interceptions * 10 \
                                + defending_overall_penalties_won * 4 \
                                + defending_overall_air_duels_won * 2 \
                                + defending_overall_blocks * 2
    logger.debug(f'積極性要素 {stats_item_aggression_buf}')

    stats_item_aggression_linear_func_x = [0, 50]  # 第1成績調整
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
            stats['shooting']['overall'].get('shots', 0)
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
            stats['defending']['overall'].get('clearance', 0),
            stats['shooting']['overall'].get('shots_on_target', 0),
            stats['shooting']['overall'].get('shots', 0),
            stats['possession']['overall'].get('dribbles_completed', 0),
            stats['possession']['overall'].get('dribbles', 0)
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


def get_player_ovr(attr: dict) -> dict:
    return {
        'WG': attr["finishing"] * 0.13
              + attr["att_positioning"] * 0.1
              + attr["short_passing"] * 0.05
              + attr["long_passing"] * 0.02
              + attr["vision"] * 0.03
              + attr["crossing"] * 0.08
              + attr["agility"] * 0.1
              + attr["ball_control"] * 0.07
              + attr["dribbling"] * 0.07
              + attr["composure"] * 0.06
              + attr["interceptions"] * 0.03
              + attr["awareness"] * 0.01
              + attr["standing_tackle"] * 0.03
              + attr["sliding_tackle"] * 0.03
              + attr["jump"] * 0.03
              + attr["stamina"] * 0.08
              + attr["strength"] * 0.04
              + attr["aggression"] * 0.04,
        'ST': attr["finishing"] * 0.15
              + attr["att_positioning"] * 0.13
              + attr["short_passing"] * 0.05
              + attr["long_passing"] * 0.02
              + attr["vision"] * 0.03
              + attr["crossing"] * 0.02
              + attr["agility"] * 0.11
              + attr["ball_control"] * 0.09
              + attr["dribbling"] * 0.08
              + attr["composure"] * 0.1
              + attr["interceptions"] * 0.02
              + attr["awareness"] * 0.01
              + attr["standing_tackle"] * 0.02
              + attr["sliding_tackle"] * 0.02
              + attr["jump"] * 0.05
              + attr["stamina"] * 0.04
              + attr["strength"] * 0.03
              + attr["aggression"] * 0.03,
        'CF': attr["finishing"] * 0.12
              + attr["att_positioning"] * 0.13
              + attr["short_passing"] * 0.07
              + attr["long_passing"] * 0.04
              + attr["vision"] * 0.04
              + attr["crossing"] * 0.02
              + attr["agility"] * 0.1
              + attr["ball_control"] * 0.07
              + attr["dribbling"] * 0.07
              + attr["composure"] * 0.08
              + attr["interceptions"] * 0.02
              + attr["awareness"] * 0.01
              + attr["standing_tackle"] * 0.02
              + attr["sliding_tackle"] * 0.02
              + attr["jump"] * 0.04
              + attr["stamina"] * 0.06
              + attr["strength"] * 0.04
              + attr["aggression"] * 0.05,
        'SMF': attr["finishing"] * 0.07
               + attr["att_positioning"] * 0.06
               + attr["short_passing"] * 0.1
               + attr["long_passing"] * 0.05
               + attr["vision"] * 0.07
               + attr["crossing"] * 0.08
               + attr["agility"] * 0.08
               + attr["ball_control"] * 0.08
               + attr["dribbling"] * 0.09
               + attr["composure"] * 0.04
               + attr["interceptions"] * 0.04
               + attr["awareness"] * 0.01
               + attr["standing_tackle"] * 0.04
               + attr["sliding_tackle"] * 0.04
               + attr["jump"] * 0.03
               + attr["stamina"] * 0.08
               + attr["strength"] * 0.02
               + attr["aggression"] * 0.02,
        'CAM': attr["finishing"] * 0.05
               + attr["att_positioning"] * 0.07
               + attr["short_passing"] * 0.12
               + attr["long_passing"] * 0.09
               + attr["vision"] * 0.14
               + attr["crossing"] * 0.02
               + attr["agility"] * 0.08
               + attr["ball_control"] * 0.07
               + attr["dribbling"] * 0.1
               + attr["composure"] * 0.06
               + attr["interceptions"] * 0.02
               + attr["awareness"] * 0.01
               + attr["standing_tackle"] * 0.02
               + attr["sliding_tackle"] * 0.02
               + attr["jump"] * 0.02
               + attr["stamina"] * 0.07
               + attr["strength"] * 0.01
               + attr["aggression"] * 0.03,
        'CM': attr["finishing"] * 0.03
              + attr["att_positioning"] * 0.05
              + attr["short_passing"] * 0.13
              + attr["long_passing"] * 0.1
              + attr["vision"] * 0.15
              + attr["crossing"] * 0.02
              + attr["agility"] * 0.08
              + attr["ball_control"] * 0.07
              + attr["dribbling"] * 0.1
              + attr["composure"] * 0.05
              + attr["interceptions"] * 0.03
              + attr["awareness"] * 0.02
              + attr["standing_tackle"] * 0.02
              + attr["sliding_tackle"] * 0.02
              + attr["jump"] * 0.02
              + attr["stamina"] * 0.07
              + attr["strength"] * 0.01
              + attr["aggression"] * 0.03,
        'DM': attr["finishing"] * 0.03
              + attr["att_positioning"] * 0.03
              + attr["short_passing"] * 0.09
              + attr["long_passing"] * 0.09
              + attr["vision"] * 0.08
              + attr["crossing"] * 0.02
              + attr["agility"] * 0.05
              + attr["ball_control"] * 0.05
              + attr["dribbling"] * 0.06
              + attr["composure"] * 0.04
              + attr["interceptions"] * 0.07
              + attr["awareness"] * 0.03
              + attr["standing_tackle"] * 0.08
              + attr["sliding_tackle"] * 0.08
              + attr["jump"] * 0.05
              + attr["stamina"] * 0.06
              + attr["strength"] * 0.04
              + attr["aggression"] * 0.05,
        'CB': attr["finishing"] * 0.03
              + attr["att_positioning"] * 0.03
              + attr["short_passing"] * 0.06
              + attr["long_passing"] * 0.06
              + attr["vision"] * 0.05
              + attr["crossing"] * 0.01
              + attr["agility"] * 0.04
              + attr["ball_control"] * 0.05
              + attr["dribbling"] * 0.05
              + attr["composure"] * 0.03
              + attr["interceptions"] * 0.1
              + attr["awareness"] * 0.04
              + attr["standing_tackle"] * 0.1
              + attr["sliding_tackle"] * 0.1
              + attr["jump"] * 0.08
              + attr["stamina"] * 0.03
              + attr["strength"] * 0.07
              + attr["aggression"] * 0.07,
        'SB': attr["finishing"] * 0.03
              + attr["att_positioning"] * 0.03
              + attr["short_passing"] * 0.1
              + attr["long_passing"] * 0.08
              + attr["vision"] * 0.05
              + attr["crossing"] * 0.06
              + attr["agility"] * 0.06
              + attr["ball_control"] * 0.06
              + attr["dribbling"] * 0.08
              + attr["composure"] * 0.03
              + attr["interceptions"] * 0.06
              + attr["awareness"] * 0.03
              + attr["standing_tackle"] * 0.07
              + attr["sliding_tackle"] * 0.07
              + attr["jump"] * 0.04
              + attr["stamina"] * 0.08
              + attr["strength"] * 0.02
              + attr["aggression"] * 0.05,
        'WB': attr["finishing"] * 0.04
              + attr["att_positioning"] * 0.03
              + attr["short_passing"] * 0.1
              + attr["long_passing"] * 0.08
              + attr["vision"] * 0.05
              + attr["crossing"] * 0.07
              + attr["agility"] * 0.07
              + attr["ball_control"] * 0.07
              + attr["dribbling"] * 0.09
              + attr["composure"] * 0.03
              + attr["interceptions"] * 0.05
              + attr["awareness"] * 0.02
              + attr["standing_tackle"] * 0.05
              + attr["sliding_tackle"] * 0.05
              + attr["jump"] * 0.04
              + attr["stamina"] * 0.08
              + attr["strength"] * 0.02
              + attr["aggression"] * 0.06,
    }


def main():
    logger.setLevel(logging.INFO)
    with open(sys.argv[1], 'r') as fp:
        player_stats_info_list = json.load(fp)
        # player_attr_list = [get_player_attr(player_stats_info) for player_stats_info in player_stats_info_list]
        # player_ovr_list = [get_player_ovr(player_attr) for player_attr in player_attr_list]
    # plt.hist([player_ovr[sys.argv[2]] for player_ovr in player_ovr_list], range=[30, 99], bins=69)

    player_stats_info_list = ave(player_stats_info_list)

    position_types = [
        "ST",
        "FW",
        "WG",
        "SMF",
        "CAM",
        "CM",
        "DM",
        "SB",
        "CB",
        "GK",
    ]

    fig, axes = plt.subplots(nrows=2, ncols=5)
    for idx, ax in enumerate(axes.ravel()):
        position_type = position_types[idx]
        ax.hist(
            [
                calc_finishing(player_stats_info['stats'])
                for player_stats_info in player_stats_info_list if player_stats_info['position_type'] == position_type
            ],
            range=[0, 100],
            bins=50
        )
        ax.set_title(position_type)
    plt.tight_layout()
    plt.show()


def ave(player_stats_info_list):
    return [
        {
            **player_stats_info,
            'position_type': max(player_stats_info['position_type'], key=player_stats_info['position_type'].get),
            'stats': {
                "shooting": {
                    "types": {
                        k: v / np.sum(list(player_stats_info['position_type'].values()))
                        for k, v in player_stats_info['stats']['shooting']['types'].items()
                    },
                    "overall": {
                        k: v / np.sum(list(player_stats_info['position_type'].values()))
                        for k, v in player_stats_info['stats']['shooting']['overall'].items()
                    },
                },
                "passing": {
                    "types": {
                        k: v / np.sum(list(player_stats_info['position_type'].values()))
                        for k, v in player_stats_info['stats']['passing']['types'].items()
                    },
                    "overall": {
                        k: v / np.sum(list(player_stats_info['position_type'].values()))
                        for k, v in player_stats_info['stats']['passing']['overall'].items()
                    },
                },
                "summary": {
                    k: v / np.sum(list(player_stats_info['position_type'].values()))
                    for k, v in player_stats_info['stats']['summary'].items()
                },
                "goalkeeping": {
                    "types": {
                        k: v / np.sum(list(player_stats_info['position_type'].values()))
                        for k, v in player_stats_info['stats']['goalkeeping']['types'].items()
                    },
                    "overall": {
                        k: v / np.sum(list(player_stats_info['position_type'].values()))
                        for k, v in player_stats_info['stats']['goalkeeping']['overall'].items()
                    },
                },
                "defending": {
                    "infractions": {
                        k: v / np.sum(list(player_stats_info['position_type'].values()))
                        for k, v in player_stats_info['stats']['defending']['infractions'].items()
                    },
                    "overall": {
                        k: v / np.sum(list(player_stats_info['position_type'].values()))
                        for k, v in player_stats_info['stats']['defending']['overall'].items()
                    },
                },
                "possession": {
                    "types": {
                        k: v / np.sum(list(player_stats_info['position_type'].values()))
                        for k, v in player_stats_info['stats']['possession']['types'].items()
                    },
                    "overall": {
                        k: v / np.sum(list(player_stats_info['position_type'].values()))
                        for k, v in player_stats_info['stats']['possession']['overall'].items()
                    },
                }
            }
        }
        for player_stats_info in player_stats_info_list if 'position_type' in player_stats_info
    ]


if __name__ == '__main__':
    main()
