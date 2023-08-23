from datetime import datetime
from itertools import product
from random import shuffle
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import models
from enums import PlayerActionEnum


def create_board_game_positions_random(table_size: int = 50):
    positions = list(product(range(1, table_size + 1), repeat=2))
    shuffle(positions)
    return positions


def placement_objects_board(dinosaurs_num: int = 50,
                            robots_num: int = 10):
    """
    This function get number of dinosaurs and robots and calculate random positions for objects in the board,
    and return their positions
    :param dinosaurs_num:
    :param robots_num:
    :return:
    """
    positions = create_board_game_positions_random()
    robots_positions, dinosaurs_positions = positions[:robots_num], \
        positions[robots_num:dinosaurs_num + robots_num]
    return robots_positions, dinosaurs_positions


async def exists_board_game(db: AsyncSession):
    exists_board_game_statement = select(models.BoardGame)
    res = await db.execute(exists_board_game_statement)
    return res.scalars().all()


async def exists_objects(db: AsyncSession):
    exists_dinosaurs = select(models.Dinosaur)
    exists_robots = select(models.Robot)
    res_dinosaurs = await db.execute(exists_robots)
    res_robots = await db.execute(exists_dinosaurs)
    return all([bool(res_robots.scalars().all()), bool(res_dinosaurs.scalars().all())])


async def is_finished_exists_board(db: AsyncSession):
    board_game_statement = select(models.BoardGame).filter(models.BoardGame.finished == True)
    exists = await db.execute(board_game_statement)
    return exists.scalars().all()


async def create_new_game(db: AsyncSession):
    new_board_game = models.BoardGame()
    await placement_objects_in_board(db, new_board_game)


async def placement_objects_in_board(db: AsyncSession,
                                     create_board_game=None,
                                     prev_board_game: models.BoardGame = None):
    robots_positions, dinosaurs_positions = placement_objects_board()
    objects = list()
    for position in robots_positions:
        objects.append(models.Robot(
            x_position=position[0],
            y_position=position[1],
        ))
    for position in dinosaurs_positions:
        objects.append(models.Dinosaur(
            x_position=position[0],
            y_position=position[1],
        ))
    if create_board_game:
        objects.append(create_board_game)
    db.add_all(objects)
    await db.commit()


async def update_for_new_game(db: AsyncSession, board_game_is_finished: bool):
    # objects_for_delete = list()
    board_game_statement = select(models.BoardGame).filter(models.BoardGame.finished == board_game_is_finished)
    result = await db.execute(board_game_statement)
    board_game = result.scalar()
    board_game.finished = False
    board_game.created = datetime.utcnow()
    # board_game.id += 1
    dinosaurs_statement = select(models.Dinosaur)
    dinosaurs_result = await db.execute(dinosaurs_statement)
    dinosaurs = list(dinosaurs_result.scalars().all())
    robots_positions, dinosaurs_positions = placement_objects_board()
    for i, dinosaur in enumerate(dinosaurs):
        dinosaur.x_position = dinosaurs_positions[i][0]
        dinosaur.y_position = dinosaurs_positions[i][1]
        dinosaur.killed = False
        # dinosaur.id += len(dinosaurs)
    robots_statement = select(models.Robot)
    robots_result = await db.execute(robots_statement)
    robots = list(robots_result.scalars().all())
    for i, robot in enumerate(robots):
        robot.x_position = robots_positions[i][0]
        robot.y_position = robots_positions[i][1]
        # robot.id += len(robots)
    await db.commit()


async def start_game(db: AsyncSession):
    exists_player = select(models.Player)
    res = await db.execute(exists_player)
    if not res.scalars().all():
        player = models.Player()
        db.add(player)
    board_game_exists = await exists_board_game(db)
    if board_game_exists:
        is_finished = await is_finished_exists_board(db)
        if is_finished:
            try:
                await update_for_new_game(db, True)
            except Exception as e:
                print(str(e))
        else:
            try:
                await update_for_new_game(db, False)
            except Exception as e:
                print(str(e))
    else:
        await create_new_game(db)



async def return_created_board_game(db: AsyncSession):
    board_game_statement = select(models.BoardGame).filter(models.BoardGame.finished == False)
    board_game_result = await db.execute(board_game_statement)
    board_game = board_game_result.scalar()
    return board_game


async def do_action(data, db: AsyncSession):
    board_game_statement = select(models.BoardGame).filter(models.BoardGame.finished == False)
    board_game_result = await db.execute(board_game_statement)
    board_game = board_game_result.scalar()
    player_statement = select(models.Player).filter(models.Player.id == data.player_id)
    result_player = await db.execute(player_statement)
    player = result_player.scalar()
    if not board_game:
        return {
            'message': f'Sorry Player (id: {player.id}) Game has finished before.'
        }

    if not player:
        raise HTTPException(status_code=403, detail="Your not a real player")
    robot_statement = select(models.Robot).filter(models.Robot.id == data.robot_id)
    result_robot = await db.execute(robot_statement)
    robot = result_robot.scalar()
    player_action: PlayerActionEnum = data.action
    robot_position: tuple = robot.x_position, robot.y_position
    robots_positions, dinosaurs_positions, objects_positions, killed_dinosaurs = await get_object_positions(db)
    check_action = await check_banned_actions(robot_position, player_action, objects_positions)
    if not check_action:
        raise HTTPException(status_code=403,
                            detail="Your movement is not acceptable")
    else:
        move_robot_response = {
            'player': player.id,
            'robot': robot.id,
            'new_robot_position': (robot.x_position, robot.y_position)
        }
        if player_action == PlayerActionEnum.UP:
            robot.y_position += 1
            return move_robot_response
        if player_action == PlayerActionEnum.DOWN:
            robot.y_position -= 1
            return move_robot_response
        if player_action == PlayerActionEnum.RIGHT:
            robot.x_position += 1
            return move_robot_response
        if player_action == PlayerActionEnum.LEFT:
            robot.x_position -= 1
            return move_robot_response
        if player_action == PlayerActionEnum.KILL:
            killed_dinosaurs_x = list(filter(lambda x: x[0] == robot.x_position, dinosaurs_positions))
            killed_dinosaurs_y = list(filter(lambda x: x[1] == robot.y_position, dinosaurs_positions))
            killed_dinosaurs_x = list(filter(lambda x: robot.y_position in [x[1] + 1, x[1] - 1], killed_dinosaurs_x))
            killed_dinosaurs_y = list(filter(lambda x: robot.x_position in [x[0] + 1, x[0] - 1], killed_dinosaurs_y))
            killed_dinosaurs = killed_dinosaurs_x + killed_dinosaurs_y
            efficient_killed_dinosaurs = list()
            if killed_dinosaurs:
                for k_dinosaur in killed_dinosaurs:
                    dinosaur_statement = select(models.Dinosaur).filter(models.Dinosaur.x_position == k_dinosaur[0],
                                                                        models.Dinosaur.y_position == k_dinosaur[1])
                    result_dinosaur = await db.execute(dinosaur_statement)
                    dinosaur = result_dinosaur.scalar()
                    if not dinosaur.killed:
                        efficient_killed_dinosaurs.append(dinosaur)
                        dinosaur.killed = True
                player.point += len(efficient_killed_dinosaurs)
                if len(efficient_killed_dinosaurs) + len(killed_dinosaurs) == len(dinosaurs_positions):
                    board_game.finished = True
                    return {
                        'player': player.id,
                        'killed_dinosaurs': len(efficient_killed_dinosaurs),
                        'new_point': len(efficient_killed_dinosaurs),
                        'message': 'Congrats, You finished the game...'
                    }
            return {
                'player': player.id,
                'killed_dinosaurs': len(efficient_killed_dinosaurs),
                'new_point': player.point
            }
        await db.commit()


async def get_object_positions(db: AsyncSession):
    dinosaurs_positions = list()
    robots_positions = list()
    objects_positions = list()
    killed_dinosaurs = list()
    dinosaur_statement = select(models.Dinosaur)
    dinosaur_result = await db.execute(dinosaur_statement)
    dinosaurs: list = list(dinosaur_result.scalars().all())
    robot_statement = select(models.Robot)
    robot_result = await db.execute(robot_statement)
    robots: list = list(robot_result.scalars().all())
    for dinosaur in dinosaurs:
        dinosaurs_positions.append((dinosaur.x_position, dinosaur.y_position))
        if dinosaur.killed:
            killed_dinosaurs.append(dinosaur)
    for robot in robots:
        robots_positions.append((robot.x_position, robot.y_position))
    objects_positions.append(dinosaurs_positions)
    objects_positions.append(robots_positions)
    return robots_positions, dinosaurs_positions, objects_positions, killed_dinosaurs


async def check_banned_actions(r_position: tuple,
                               player_action: PlayerActionEnum,
                               objects_positions: list):
    x, y = r_position
    if PlayerActionEnum.RIGHT == player_action:
        if x == 50:
            return False
        new_pos = (x + 1, y)
        if new_pos in objects_positions:
            return False
    if PlayerActionEnum.LEFT == player_action:
        if x == 1:
            return False
        new_pos = (x - 1, y)
        if new_pos in objects_positions:
            return False
    if PlayerActionEnum.UP == player_action:
        if y == 50:
            return False
        new_pos = (x, y + 1)
        if new_pos in objects_positions:
            return False
    if PlayerActionEnum.DOWN == player_action:
        if y == 1:
            return False
        new_pos = (x, y - 1)
        if new_pos in objects_positions:
            return False
    return True
