import pygame
import sys
import os
from typing import List, Dict, Optional

# Pygame 초기화
pygame.init()

# 화면 설정
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("금지 구역 - 폐병원 방탈출")

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
GRAY = (64, 64, 64)
DARK_GRAY = (32, 32, 32)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# 에셋 폴더
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# 폰트 설정 (한글 지원)
try:
    font_large = pygame.font.SysFont('malgun gothic', 48)
    font_medium = pygame.font.SysFont('malgun gothic', 32)
    font_small = pygame.font.SysFont('malgun gothic', 24)
    font_tiny = pygame.font.SysFont('malgun gothic', 18)
except:
    try:
        font_large = pygame.font.SysFont('gulim', 48)
        font_medium = pygame.font.SysFont('gulim', 32)
        font_small = pygame.font.SysFont('gulim', 24)
        font_tiny = pygame.font.SysFont('gulim', 18)
    except:
        font_large = pygame.font.SysFont('arial', 48)
        font_medium = pygame.font.SysFont('arial', 32)
        font_small = pygame.font.SysFont('arial', 24)
        font_tiny = pygame.font.SysFont('arial', 18)

class Item:
    def __init__(self, name: str, description: str, image_key: str = None):
        self.name = name
        self.description = description
        self.image_key = image_key
        self.used = False

class Inventory:
    def __init__(self):
        self.items: List[Item] = []
        self.max_items = 8
        
    def add_item(self, item: Item) -> bool:
        if len(self.items) < self.max_items:
            self.items.append(item)
            return True
        return False
        
    def remove_item(self, item_name: str) -> Optional[Item]:
        for i, item in enumerate(self.items):
            if item.name == item_name:
                return self.items.pop(i)
        return None
        
    def has_item(self, item_name: str) -> bool:
        return any(item.name == item_name for item in self.items)
        
    def use_item(self, item_name: str) -> bool:
        for item in self.items:
            if item.name == item_name and not item.used:
                item.used = True
                return True
        return False

class MainMenu:
    def __init__(self):
        self.selected_option = 0
        self.menu_options = ["게임 시작", "게임 종료"]
        
    def draw(self):
        screen.fill(BLACK)
        
        title = font_large.render("금지 구역", True, RED)
        subtitle = font_medium.render("폐병원 방탈출", True, WHITE)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60))
        
        screen.blit(title, title_rect)
        screen.blit(subtitle, subtitle_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option in enumerate(self.menu_options):
            text = font_medium.render(option, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 60))
            
            click_rect = pygame.Rect(text_rect.x - 50, text_rect.y - 10, text_rect.width + 100, text_rect.height + 20)
            
            is_hovered = click_rect.collidepoint(mouse_pos)
            is_selected = i == self.selected_option
            
            if is_hovered or is_selected:
                color = RED
                box_rect = pygame.Rect(text_rect.x - 20, text_rect.y - 10, text_rect.width + 40, text_rect.height + 20)
                pygame.draw.rect(screen, DARK_RED, box_rect)
                pygame.draw.rect(screen, RED, box_rect, 3)
            else:
                color = WHITE
            
            text = font_medium.render(option, True, color)
            screen.blit(text, text_rect)
        
        instruction = font_small.render("방향키 또는 마우스로 선택, Enter 또는 클릭으로 확인", True, GRAY)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(instruction, instruction_rect)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                return self.menu_options[self.selected_option]
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(self.menu_options):
                    text = font_medium.render(option, True, WHITE)
                    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 60))
                    click_rect = pygame.Rect(text_rect.x - 50, text_rect.y - 10, text_rect.width + 100, text_rect.height + 20)
                    if click_rect.collidepoint(mouse_pos):
                        return option
        return None

class EscapeRoom:
    def __init__(self):
        self.current_room = "exterior"
        self.inventory = Inventory()
        self.game_state = "playing"  # playing, escaped, game_over
        self.message = ""
        self.message_timer = 0
        
        # 배경 이미지
        self.backgrounds = {
            "exterior": DARK_GRAY,
            "lobby": BLACK,
            "corridor": DARK_GRAY,
            "ward": BLACK,
            "operating": BLACK,
            "morgue": BLACK,
            "security": DARK_GRAY,
            "stairs": DARK_GRAY
        }
        
        self.bg_images: Dict[str, Optional[pygame.Surface]] = {}
        print("배경 이미지를 로딩하고 있습니다...")
        for key in self.backgrounds.keys():
            self.bg_images[key] = self._try_load_bg_image(key)
            if self.bg_images[key]:
                print(f"✓ {key}.jpg 로딩 완료")
            else:
                print(f"⚠ {key}.jpg 없음 - 색상 배경 사용")
        print("배경 이미지 로딩 완료!")
        
        # 아이템 정의
        self.items = {
            "열쇠": Item("열쇠", "낡은 열쇠. 어딘가의 문을 열 수 있을 것 같다."),
            "전지": Item("전지", "AA 전지. 전자기기에 사용할 수 있다."),
            "테이프": Item("테이프", "낡은 VHS 테이프. 녹화된 내용이 있을 것 같다."),
            "의료기록": Item("의료기록", "환자의 의료기록. 중요한 정보가 담겨있다."),
            "카드키": Item("카드키", "보안 카드키. 특정 문을 열 수 있다."),
            "지도": Item("지도", "병원 지도. 출구를 찾는 데 도움이 될 것이다."),
            "손전등": Item("손전등", "휴대용 손전등. 어둠을 밝힐 수 있다."),
            "비상등": Item("비상등", "비상 탈출구용 등. 탈출할 때 사용한다."),
            "탈출열쇠": Item("탈출열쇠", "비상 탈출구용 열쇠. 시체안치실에서 사용할 수 있다.")
        }
        
        # 방별 설정
        self.rooms = {
            "exterior": {
                "name": "병원 외부",
                "description": "버려진 병원 앞. 차가운 바람이 휘돈다. 정문이 잠겨있다.",
                "items": ["열쇠"],
                "interactions": ["정문 열기"],
                "exits": []
            },
            "lobby": {
                "name": "로비",
                "description": "로비에는 먼지 냄새와 곰팡이 냄새가 섞여 있다. 붉은 비상등이 깜빡인다.",
                "items": ["지도"],
                "interactions": ["비상등 확인"],
                "exits": ["corridor", "security"]
            },
            "corridor": {
                "name": "복도",
                "description": "긴 복도 끝에서 금속이 끄는 소리가 들린다. 휠체어가 혼자 움직이는 듯 흔들린다.",
                "items": [],
                "interactions": ["휠체어 확인"],
                "exits": ["lobby", "ward", "operating", "stairs"]
            },
            "security": {
                "name": "보안실",
                "description": "보안실. 꺼진 모니터가 줄지어 있고, 낡은 영상기록 장치가 덩그러니 놓여 있다.",
                "items": ["테이프"],
                "interactions": ["모니터 켜기", "테이프 재생"],
                "exits": ["lobby"],
                "requires": {"카드키": "카드키가 필요하다."}
            },
            "ward": {
                "name": "병동",
                "description": "병동 병실. 커튼이 바람도 없는데 가볍게 흔들린다. 금고가 있는 서랍이 있다.",
                "items": ["의료기록"],
                "interactions": ["커튼 확인", "병상 확인", "서랍 열기"],
                "exits": ["corridor"]
            },
            "operating": {
                "name": "수술실",
                "description": "수술실. 작업등 몇 개가 아직 살아 있다. 바닥에는 오래된 얼룩이 남아 있다.",
                "items": ["전지"],
                "interactions": ["수술대 확인", "도구함 열기"],
                "exits": ["corridor"]
            },
            "stairs": {
                "name": "계단",
                "description": "계단실. 아래로 내려갈수록 공기가 차갑고 무거워진다.",
                "items": ["손전등"],
                "interactions": ["지하 내려가기"],
                "exits": ["corridor", "morgue"]
            },
            "morgue": {
                "name": "시체안치실",
                "description": "시체안치실. 서랍 몇 개가 반쯤 열려 있다. 이름표가 떨리는 듯 흔들린다. 벽에 비상 탈출구가 있다.",
                "items": ["카드키", "비상등"],
                "interactions": ["서랍 확인", "비상 탈출구 열기", "비상등 설치", "열쇠 사용"],
                "exits": ["stairs"],
                "requires": {"손전등": "어둡다. 손전등이 필요하다."}
            }
        }
        
        # 퍼즐 상태
        self.puzzles = {
            "security_monitor": False,  # 보안실 모니터 켜짐
            "tape_played": False,       # 테이프 재생됨
            "password_revealed": False, # 비밀번호 발견됨
            "drawer_opened": False,     # 서랍 열림
            "exit_ready": False         # 탈출구 준비됨
        }
        
    def _try_load_bg_image(self, key: str) -> Optional[pygame.Surface]:
        for ext in (".jpg", ".png", ".jpeg"):
            path = os.path.join(ASSETS_DIR, f"{key}{ext}")
            if os.path.isfile(path):
                try:
                    img = pygame.image.load(path).convert()
                    return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                except Exception:
                    return None
        return None
    
    def show_message(self, message: str, duration: int = 120):
        self.message = message
        self.message_timer = duration
    
    def can_enter_room(self, room_name: str) -> tuple[bool, str]:
        room = self.rooms[room_name]
        if "requires" in room:
            for item, message in room["requires"].items():
                if not self.inventory.has_item(item):
                    return False, message
        return True, ""
    
    def move_to_room(self, room_name: str):
        can_enter, message = self.can_enter_room(room_name)
        if can_enter:
            self.current_room = room_name
            self.show_message(f"{self.rooms[room_name]['name']}에 도착했다.")
        else:
            self.show_message(message)
    
    def collect_item(self, item_name: str):
        if item_name in self.items and item_name in self.rooms[self.current_room]["items"]:
            if self.inventory.add_item(self.items[item_name]):
                self.rooms[self.current_room]["items"].remove(item_name)
                self.show_message(f"{item_name}을(를) 획득했다!")
            else:
                self.show_message("인벤토리가 가득 찼다.")
        else:
            self.show_message("그런 아이템은 없다.")
    
    def use_item(self, item_name: str):
        if not self.inventory.has_item(item_name):
            self.show_message("그런 아이템은 없다.")
            return
        
        # 특정 아이템 사용 로직
        if item_name == "열쇠" and self.current_room == "exterior":
            self.move_to_room("lobby")
            self.inventory.remove_item("열쇠")
        elif item_name == "전지" and self.current_room == "security":
            if not self.puzzles["security_monitor"]:
                self.puzzles["security_monitor"] = True
                self.show_message("모니터가 켜졌다!")
                self.inventory.remove_item("전지")
            else:
                self.show_message("모니터가 이미 켜져 있다.")
        elif item_name == "테이프" and self.current_room == "security":
            if self.puzzles["security_monitor"]:
                if not self.puzzles["tape_played"]:
                    self.puzzles["tape_played"] = True
                    self.show_message("테이프에서 중요한 정보를 발견했다!")
                    self.inventory.remove_item("테이프")
                else:
                    self.show_message("테이프를 이미 재생했다.")
            else:
                self.show_message("먼저 모니터를 켜야 한다.")
        elif item_name == "손전등":
            self.show_message("손전등은 시체안치실에 들어가기 위해 필요하다.")
        elif item_name == "비상등" and self.current_room == "morgue":
            self.show_message("비상등을 설치하려면 '비상등 설치' 버튼을 클릭하세요.")
        elif item_name == "탈출열쇠" and self.current_room == "morgue":
            self.show_message("탈출열쇠를 사용하려면 '열쇠 사용' 버튼을 클릭하세요.")
        elif item_name == "카드키":
            if self.current_room == "lobby":
                self.show_message("카드키로 보안실 문을 열 수 있다.")
            elif self.current_room == "security":
                self.show_message("보안실에 이미 들어왔다.")
            else:
                self.show_message("카드키는 보안실에서 사용할 수 있다.")
        elif item_name == "지도":
            self.show_message("병원 지도: 외부 → 로비 → 복도 → 보안실/병동/수술실/계단 → 시체안치실")
        elif item_name == "의료기록":
            self.show_message("의료기록에는 '환자 관찰 중'이라는 기록이 있다.")
        else:
            self.show_message(f"{item_name}을(를) 여기서 사용할 수 없다.")
    
    def interact(self, interaction: str):
        room = self.rooms[self.current_room]
        
        if interaction == "정문 열기" and self.current_room == "exterior":
            if self.inventory.has_item("열쇠"):
                self.show_message("정문이 열렸다! 로비로 들어갈 수 있다.")
                # 정문을 열면 로비로 이동할 수 있게 함
                self.rooms["exterior"]["exits"] = ["lobby"]
            else:
                self.show_message("열쇠가 필요하다.")
        elif interaction == "출구 찾기" and self.current_room == "lobby":
            self.show_message("정문은 잠겨있다. 다른 출구를 찾아야 한다.")
        elif interaction == "비상등 확인" and self.current_room == "lobby":
            self.show_message("비상등이 깜빡인다. 무언가를 알려주는 것 같다.")
        elif interaction == "휠체어 확인" and self.current_room == "corridor":
            self.show_message("휠체어는 아직 따뜻하다. 누군가 최근에 사용한 것 같다.")
        elif interaction == "모니터 켜기" and self.current_room == "security":
            if self.puzzles["security_monitor"]:
                self.show_message("모니터가 이미 켜져 있다.")
            elif self.inventory.has_item("전지"):
                self.puzzles["security_monitor"] = True
                self.show_message("모니터가 켜졌다!")
                self.inventory.remove_item("전지")
            else:
                self.show_message("전지가 필요하다.")
        elif interaction == "테이프 재생" and self.current_room == "security":
            if self.puzzles["tape_played"]:
                self.show_message("테이프를 이미 재생했다.")
            elif self.puzzles["security_monitor"] and self.inventory.has_item("테이프"):
                self.puzzles["tape_played"] = True
                self.puzzles["password_revealed"] = True
                self.show_message("테이프에서 비밀번호를 발견했다: 1-9-7-3")
                self.inventory.remove_item("테이프")
            elif not self.puzzles["security_monitor"]:
                self.show_message("먼저 모니터를 켜야 한다.")
            else:
                self.show_message("테이프가 필요하다.")
        elif interaction == "커튼 확인" and self.current_room == "ward":
            self.show_message("커튼 뒤에는 아무것도 없다.")
        elif interaction == "병상 확인" and self.current_room == "ward":
            self.show_message("병상에는 오래된 시트만 깔려있다.")
        elif interaction == "서랍 열기" and self.current_room == "ward":
            if self.puzzles["password_revealed"]:
                if not self.puzzles["drawer_opened"]:
                    self.puzzles["drawer_opened"] = True
                    self.show_message("서랍이 열렸다! 탈출열쇠를 발견했다!")
                    # 탈출열쇠를 바로 인벤토리에 추가
                    if self.inventory.add_item(self.items["탈출열쇠"]):
                        self.show_message("탈출열쇠를 획득했다!")
                    else:
                        self.show_message("인벤토리가 가득 찼다.")
                else:
                    self.show_message("서랍은 이미 열려있다.")
            else:
                self.show_message("잠겨있다.")
        elif interaction == "수술대 확인" and self.current_room == "operating":
            self.show_message("수술대에는 오래된 얼룩이 남아있다.")
        elif interaction == "도구함 열기" and self.current_room == "operating":
            self.show_message("도구함은 비어있다.")
        elif interaction == "지하 내려가기" and self.current_room == "stairs":
            self.move_to_room("morgue")
        elif interaction == "서랍 확인" and self.current_room == "morgue":
            if "카드키" in room["items"]:
                self.show_message("서랍에서 카드키를 발견했다!")
                if self.inventory.add_item(self.items["카드키"]):
                    self.rooms[self.current_room]["items"].remove("카드키")
                    self.show_message("카드키를 획득했다!")
                else:
                    self.show_message("인벤토리가 가득 찼다.")
            else:
                self.show_message("서랍은 이미 비어있다.")
        elif interaction == "비상등 설치" and self.current_room == "morgue":
            if self.inventory.has_item("비상등"):
                self.puzzles["exit_ready"] = True
                self.show_message("비상등을 설치했다. 탈출구가 밝혀졌다!")
                self.inventory.remove_item("비상등")
            else:
                self.show_message("비상등이 필요하다.")
        elif interaction == "열쇠 사용" and self.current_room == "morgue":
            if self.inventory.has_item("탈출열쇠"):
                if self.puzzles["exit_ready"]:
                    self.show_message("탈출열쇠를 비상 탈출구에 끼웠다!")
                    self.inventory.remove_item("탈출열쇠")
                else:
                    self.show_message("먼저 비상등을 설치해야 한다.")
            else:
                self.show_message("탈출열쇠가 필요하다.")
        elif interaction == "비상 탈출구 열기" and self.current_room == "morgue":
            if self.puzzles["exit_ready"]:
                self.game_state = "escaped"
                self.show_message("비상 탈출구를 열고 탈출에 성공했다!", 300)
            else:
                self.show_message("비상등과 탈출열쇠가 필요하다.")
        else:
            self.show_message("그런 상호작용은 없다.")
    
    def draw_room_info(self):
        room = self.rooms[self.current_room]
        
        # 방 이름
        room_name = font_large.render(room["name"], True, WHITE)
        screen.blit(room_name, (50, 50))
        
        # 방 설명
        desc_lines = self.wrap_text(room["description"], font_medium, SCREEN_WIDTH - 100)
        for i, line in enumerate(desc_lines):
            desc_text = font_medium.render(line, True, WHITE)
            screen.blit(desc_text, (50, 120 + i * 35))
    
    def draw_inventory(self):
        # 인벤토리 배경
        inv_rect = pygame.Rect(SCREEN_WIDTH - 300, 50, 250, 400)
        pygame.draw.rect(screen, BLACK, inv_rect)
        pygame.draw.rect(screen, WHITE, inv_rect, 2)
        
        # 인벤토리 제목
        inv_title = font_medium.render("인벤토리", True, WHITE)
        screen.blit(inv_title, (SCREEN_WIDTH - 290, 60))
        
        # 아이템 목록
        for i, item in enumerate(self.inventory.items):
            item_text = font_small.render(f"• {item.name}", True, WHITE)
            screen.blit(item_text, (SCREEN_WIDTH - 280, 100 + i * 25))
    
    def draw_interactions(self):
        room = self.rooms[self.current_room]
        
        # 상호작용 버튼들
        button_y = SCREEN_HEIGHT - 200
        for i, interaction in enumerate(room["interactions"]):
            button_rect = pygame.Rect(50, button_y + i * 40, 200, 35)
            
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, DARK_RED, button_rect)
                pygame.draw.rect(screen, RED, button_rect, 2)
            else:
                pygame.draw.rect(screen, GRAY, button_rect)
                pygame.draw.rect(screen, WHITE, button_rect, 2)
            
            button_text = font_small.render(interaction, True, WHITE)
            text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, text_rect)
        
        # 디버깅: 상호작용 버튼 개수 표시
        debug_text = font_tiny.render(f"상호작용 버튼: {len(room['interactions'])}개", True, YELLOW)
        screen.blit(debug_text, (50, SCREEN_HEIGHT - 250))
    
    def draw_items(self):
        room = self.rooms[self.current_room]
        
        if room["items"]:
            items_text = font_medium.render("획득 가능한 아이템:", True, YELLOW)
            screen.blit(items_text, (50, SCREEN_HEIGHT - 350))
            
            for i, item_name in enumerate(room["items"]):
                item_rect = pygame.Rect(50, SCREEN_HEIGHT - 320 + i * 40, 200, 35)
                
                mouse_pos = pygame.mouse.get_pos()
                if item_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, GREEN, item_rect)
                    pygame.draw.rect(screen, WHITE, item_rect, 2)
                else:
                    pygame.draw.rect(screen, DARK_GRAY, item_rect)
                    pygame.draw.rect(screen, WHITE, item_rect, 2)
                
                item_text = font_small.render(item_name, True, WHITE)
                text_rect = item_text.get_rect(center=item_rect.center)
                screen.blit(item_text, text_rect)
    
    def draw_exits(self):
        room = self.rooms[self.current_room]
        
        exits_text = font_medium.render("이동 가능한 곳:", True, GREEN)
        screen.blit(exits_text, (300, SCREEN_HEIGHT - 200))
        
        for i, exit_room in enumerate(room["exits"]):
            exit_rect = pygame.Rect(300, SCREEN_HEIGHT - 170 + i * 40, 200, 35)
            
            mouse_pos = pygame.mouse.get_pos()
            if exit_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, GREEN, exit_rect)
                pygame.draw.rect(screen, WHITE, exit_rect, 2)
            else:
                pygame.draw.rect(screen, DARK_GRAY, exit_rect)
                pygame.draw.rect(screen, WHITE, exit_rect, 2)
            
            exit_text = font_small.render(self.rooms[exit_room]["name"], True, WHITE)
            text_rect = exit_text.get_rect(center=exit_rect.center)
            screen.blit(exit_text, text_rect)
    
    def draw_message(self):
        if self.message_timer > 0:
            message_bg = pygame.Rect(50, SCREEN_HEIGHT - 100, SCREEN_WIDTH - 100, 40)
            pygame.draw.rect(screen, BLACK, message_bg)
            pygame.draw.rect(screen, WHITE, message_bg, 2)
            
            message_text = font_small.render(self.message, True, WHITE)
            text_rect = message_text.get_rect(center=message_bg.center)
            screen.blit(message_text, text_rect)
            
            self.message_timer -= 1
    
    def draw_ending(self):
        if self.game_state == "escaped":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            title = font_large.render("탈출 성공!", True, GREEN)
            subtitle = font_medium.render("폐병원에서 무사히 탈출했다.", True, WHITE)
            instruction = font_small.render("클릭하면 게임이 종료됩니다", True, GRAY)
            
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            
            screen.blit(title, title_rect)
            screen.blit(subtitle, subtitle_rect)
            screen.blit(instruction, instruction_rect)
    
    def wrap_text(self, text: str, font, max_width: int) -> List[str]:
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def handle_click(self, pos):
        if self.game_state == "escaped":
            return "exit"
        
        # 상호작용 버튼 클릭
        room = self.rooms[self.current_room]
        button_y = SCREEN_HEIGHT - 200
        for i, interaction in enumerate(room["interactions"]):
            button_rect = pygame.Rect(50, button_y + i * 40, 200, 35)
            if button_rect.collidepoint(pos):
                self.interact(interaction)
                return None
        
        # 아이템 클릭
        if room["items"]:
            for i, item_name in enumerate(room["items"]):
                item_rect = pygame.Rect(50, SCREEN_HEIGHT - 320 + i * 40, 200, 35)
                if item_rect.collidepoint(pos):
                    self.collect_item(item_name)
                    return None
        
        # 출구 클릭
        for i, exit_room in enumerate(room["exits"]):
            exit_rect = pygame.Rect(300, SCREEN_HEIGHT - 170 + i * 40, 200, 35)
            if exit_rect.collidepoint(pos):
                self.move_to_room(exit_room)
                return None
        
        # 인벤토리 아이템 클릭 (사용)
        inv_rect = pygame.Rect(SCREEN_WIDTH - 300, 50, 250, 400)
        if inv_rect.collidepoint(pos):
            # 클릭한 위치에서 아이템 인덱스 계산
            item_y = pos[1] - 100
            item_index = item_y // 25
            if 0 <= item_index < len(self.inventory.items):
                self.use_item(self.inventory.items[item_index].name)
        
        return None
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        result = self.handle_click(event.pos)
                        if result == "exit":
                            running = False
            
            # 화면 그리기
            screen.fill(BLACK)
            
            # 배경 그리기
            bg_color = self.backgrounds[self.current_room]
            image = self.bg_images.get(self.current_room)
            
            if image is not None:
                screen.blit(image, (0, 0))
            else:
                screen.fill(bg_color)
            
            # 어둠 효과
            if self.current_room in ["lobby", "operating", "morgue", "ward", "security", "corridor", "stairs"]:
                dark_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                dark_surface.set_alpha(100)
                dark_surface.fill(BLACK)
                screen.blit(dark_surface, (0, 0))
            
            # UI 그리기
            self.draw_room_info()
            self.draw_inventory()
            self.draw_interactions()
            self.draw_items()
            self.draw_exits()
            self.draw_message()
            
            if self.game_state == "escaped":
                self.draw_ending()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    print("금지 구역 - 공포 방탈출 게임을 시작합니다...")
    print("게임을 종료하려면 창을 닫으세요.")
    
    menu = MainMenu()
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            
            result = menu.handle_input(event)
            if result == "게임 시작":
                game = EscapeRoom()
                game.run()
                menu = MainMenu()
            elif result == "게임 종료":
                running = False
                break
        
        menu.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
