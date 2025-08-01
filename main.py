import datetime
import multiprocessing
import time
import os

from worker import Worker, VideoStatus
import pygame
from config import video_ids

if __name__ == "__main__":

    os.makedirs("downloads/", exist_ok=True)
    os.makedirs("temp/", exist_ok=True)

    pygame.init()

    screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)

    process_nums = multiprocessing.cpu_count()
    workers: list[Worker] = list()

    video_id_list = list(video_ids)

    for i in range(process_nums):
        start_index = int(len(video_id_list) / process_nums * i)
        end_index = int(len(video_id_list) / process_nums * (i + 1))

        workers.append(
            Worker(video_id_list[start_index:end_index])
        )

    status_surface = pygame.Surface((max([len(worker.video_ids) for worker in workers]), len(workers)))
    complete_event_triggered = False


    start_time = time.time()
    for worker in workers:
        worker.start()


    on = True
    while on:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on = False

        is_done = True

        for worker in workers:
            if not worker.is_done:
                is_done = False

        if is_done:
            screen.fill((0, 255, 0))

            if not complete_event_triggered:
                complete_event_triggered = True

                end_time = time.time()

                elapsed_time = end_time - start_time

                print(f"응 끝났쥬?ㅋ | 소요시간: {str(datetime.timedelta(seconds=elapsed_time))}")

        else:
            screen.fill((0, 0, 0))

        for y, worker in enumerate(workers):
            worker.update_status()
            for x, video_status in enumerate(worker.video_statuses.values()):

                if video_status == VideoStatus.WAIT:
                    status_surface.set_at((x, y), (127, 127, 127))
                elif video_status == VideoStatus.MID_FAILED:
                    status_surface.set_at((x, y), (255, 255, 0))
                elif video_status == VideoStatus.COMPLETED:
                    status_surface.set_at((x, y), (0, 255, 0))
                elif video_status == VideoStatus.FAILED:
                    status_surface.set_at((x, y), (255, 0, 0))

        screen.blit(
            pygame.transform.scale(status_surface, screen.get_size()), (0, 0)
        )

        pygame.display.flip()


    for worker in workers:
        worker.process.terminate()