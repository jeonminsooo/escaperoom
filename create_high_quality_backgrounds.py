from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
import os
import random
import math

# assets 폴더 생성
if not os.path.exists('assets'):
    os.makedirs('assets')

# 화면 크기
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

def create_noise_texture(width, height, scale=50):
    """노이즈 텍스처 생성"""
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    for x in range(width):
        for y in range(height):
            noise = random.randint(0, 255)
            pixels[x, y] = (noise, noise, noise)
    
    # 블러 효과
    img = img.filter(ImageFilter.GaussianBlur(scale))
    return img

def create_gradient_overlay(width, height, color1, color2, direction='vertical'):
    """그라데이션 오버레이 생성"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    if direction == 'vertical':
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:
        for x in range(width):
            ratio = x / width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(x, 0), (x, height)], fill=(r, g, b))
    
    return img

def create_exterior():
    """병원 외부 - 고품질 어두운 병원 건물"""
    # 기본 배경 (어두운 하늘)
    sky_gradient = create_gradient_overlay(SCREEN_WIDTH, SCREEN_HEIGHT//2, (10, 10, 15), (5, 5, 8))
    
    # 병원 건물 (더 복잡한 구조)
    building = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT//2), (8, 8, 8))
    draw = ImageDraw.Draw(building)
    
    # 건물의 여러 층
    floors = 5
    floor_height = SCREEN_HEIGHT//2 // floors
    
    for floor in range(floors):
        y_start = floor * floor_height
        y_end = (floor + 1) * floor_height
        
        # 각 층마다 다른 어둠 정도
        darkness = 8 + floor * 2
        draw.rectangle([200, y_start, SCREEN_WIDTH-200, y_end], fill=(darkness, darkness, darkness))
        
        # 창문들 (더 사실적)
        windows_per_floor = 8
        for i in range(windows_per_floor):
            x = 250 + i * 100
            y = y_start + floor_height//3
            
            # 창문 프레임
            draw.rectangle([x, y, x+60, y+40], fill=(darkness+5, darkness+5, darkness+5))
            
            # 창문 유리 (어두운 노란색)
            if random.random() < 0.3:  # 30% 확률로 불이 켜진 창문
                draw.rectangle([x+5, y+5, x+55, y+35], fill=(40, 35, 20))
            else:
                draw.rectangle([x+5, y+5, x+55, y+35], fill=(darkness+2, darkness+2, darkness+2))
    
    # 입구 (더 어둡고 깊이감 있게)
    entrance_width = 200
    entrance_x = SCREEN_WIDTH//2 - entrance_width//2
    
    # 입구 계단
    for i in range(5):
        step_y = SCREEN_HEIGHT//2 + i * 10
        step_width = entrance_width + i * 20
        step_x = SCREEN_WIDTH//2 - step_width//2
        draw.rectangle([step_x, step_y, step_x+step_width, step_y+10], fill=(3, 3, 3))
    
    # 입구 문
    draw.rectangle([entrance_x, SCREEN_HEIGHT//2, entrance_x+entrance_width, SCREEN_HEIGHT], fill=(2, 2, 2))
    
    # 안개 효과 (더 자연스럽게)
    fog = Image.new('RGBA', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 0))
    fog_draw = ImageDraw.Draw(fog)
    
    for i in range(30):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(SCREEN_HEIGHT-150, SCREEN_HEIGHT)
        size = random.randint(50, 150)
        alpha = random.randint(10, 40)
        fog_draw.ellipse([x-size//2, y-size//4, x+size//2, y+size//4], fill=(100, 100, 100, alpha))
    
    # 최종 이미지 조합
    final_img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT))
    final_img.paste(sky_gradient, (0, 0))
    final_img.paste(building, (0, SCREEN_HEIGHT//2))
    final_img = Image.alpha_composite(final_img.convert('RGBA'), fog).convert('RGB')
    
    # 전체적으로 어둡게 조정
    enhancer = ImageEnhance.Brightness(final_img)
    final_img = enhancer.enhance(0.7)
    
    final_img.save('assets/exterior.jpg', quality=95)

def create_lobby():
    """로비 - 고품질 어두운 로비"""
    # 기본 배경 (어두운 벽과 바닥)
    img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), (5, 5, 5))
    draw = ImageDraw.Draw(img)
    
    # 바닥 (타일 패턴)
    tile_size = 40
    for x in range(0, SCREEN_WIDTH, tile_size):
        for y in range(SCREEN_HEIGHT-200, SCREEN_HEIGHT, tile_size):
            color = (12, 12, 12) if (x + y) % (tile_size * 2) == 0 else (8, 8, 8)
            draw.rectangle([x, y, x+tile_size, y+tile_size], fill=color)
    
    # 벽 (텍스처 추가)
    wall_noise = create_noise_texture(SCREEN_WIDTH, SCREEN_HEIGHT-200, 2)
    wall_overlay = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT-200), (8, 8, 8))
    wall_overlay = Image.blend(wall_overlay, wall_noise, 0.3)
    img.paste(wall_overlay, (0, 0))
    
    # 붉은 비상등 효과 (더 사실적)
    for i in range(4):
        x = 150 + i * 250
        y = 80
        
        # 비상등 본체
        draw.rectangle([x-15, y-10, x+15, y+10], fill=(30, 0, 0))
        
        # 빛의 확산 효과
        for j in range(8):
            radius = j * 15
            alpha = 50 - j * 5
            if alpha > 0:
                light_overlay = Image.new('RGBA', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 0))
                light_draw = ImageDraw.Draw(light_overlay)
                light_draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=(80, 0, 0, alpha))
                img = Image.alpha_composite(img.convert('RGBA'), light_overlay).convert('RGB')
    
    # 리셉션 데스크 (더 상세하게)
    desk_x = SCREEN_WIDTH//2 - 200
    desk_y = SCREEN_HEIGHT - 280
    
    # 데스크 본체
    draw.rectangle([desk_x, desk_y, desk_x+400, desk_y+60], fill=(15, 15, 15))
    
    # 데스크 상판
    draw.rectangle([desk_x, desk_y, desk_x+400, desk_y+10], fill=(25, 25, 25))
    
    # 데스크 다리들
    for i in range(4):
        leg_x = desk_x + 50 + i * 100
        draw.rectangle([leg_x, desk_y+10, leg_x+20, desk_y+60], fill=(12, 12, 12))
    
    # 먼지 입자 효과 (더 자연스럽게)
    for i in range(200):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 3)
        color = random.randint(80, 120)
        draw.ellipse([x, y, x+size, y+size], fill=(color, color, color))
    
    # 전체적으로 어둡게 조정
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.6)
    
    img.save('assets/lobby.jpg', quality=95)

def create_corridor():
    """복도 - 고품질 긴 복도"""
    img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), (20, 20, 20))
    draw = ImageDraw.Draw(img)
    
    # 천장 (조명 패널)
    ceiling_height = 80
    panel_width = 120
    for x in range(0, SCREEN_WIDTH, panel_width):
        # 조명 패널
        draw.rectangle([x, 0, x+panel_width, ceiling_height], fill=(15, 15, 15))
        # 조명 그릴
        draw.rectangle([x+10, 10, x+panel_width-10, 30], fill=(25, 25, 25))
    
    # 바닥 (린올륨 패턴)
    floor_start = SCREEN_HEIGHT - 150
    tile_width = 60
    for x in range(0, SCREEN_WIDTH, tile_width):
        for y in range(floor_start, SCREEN_HEIGHT, tile_width):
            base_color = (18, 18, 18)
            if (x + y) % (tile_width * 2) == 0:
                base_color = (22, 22, 22)
            draw.rectangle([x, y, x+tile_width, y+tile_width], fill=base_color)
    
    # 벽 (더 사실적인 텍스처)
    wall_noise = create_noise_texture(SCREEN_WIDTH, SCREEN_HEIGHT-230, 1)
    wall_overlay = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT-230), (25, 25, 25))
    wall_overlay = Image.blend(wall_overlay, wall_noise, 0.2)
    img.paste(wall_overlay, (0, ceiling_height))
    
    # 휠체어 (더 상세하게)
    wheelchair_x = SCREEN_WIDTH//2
    wheelchair_y = SCREEN_HEIGHT - 220
    
    # 휠체어 바퀴들
    wheel_radius = 25
    for wheel_x in [wheelchair_x - 20, wheelchair_x + 20]:
        # 바퀴 테두리
        draw.ellipse([wheel_x-wheel_radius, wheelchair_y-wheel_radius//2, 
                     wheel_x+wheel_radius, wheelchair_y+wheel_radius//2], fill=(35, 35, 35))
        # 바퀴 스포크들
        for i in range(8):
            angle = i * math.pi / 4
            x1 = wheel_x + int(15 * math.cos(angle))
            y1 = wheelchair_y + int(7 * math.sin(angle))
            x2 = wheel_x + int(20 * math.cos(angle))
            y2 = wheelchair_y + int(10 * math.sin(angle))
            draw.line([(x1, y1), (x2, y2)], fill=(30, 30, 30), width=2)
    
    # 휠체어 의자
    draw.rectangle([wheelchair_x-25, wheelchair_y-50, wheelchair_x+25, wheelchair_y-10], fill=(30, 30, 30))
    # 의자 등받이
    draw.rectangle([wheelchair_x-25, wheelchair_y-50, wheelchair_x+25, wheelchair_y-40], fill=(25, 25, 25))
    
    # 문들 (복도 양쪽)
    for i in range(4):
        x = 150 + i * 250
        # 문 프레임
        draw.rectangle([x, SCREEN_HEIGHT-320, x+100, SCREEN_HEIGHT-150], fill=(20, 20, 20))
        # 문
        draw.rectangle([x+5, SCREEN_HEIGHT-315, x+95, SCREEN_HEIGHT-155], fill=(15, 15, 15))
        # 문 손잡이
        draw.rectangle([x+80, SCREEN_HEIGHT-280, x+90, SCREEN_HEIGHT-270], fill=(40, 40, 40))
        # 문 번호
        draw.text((x+45, SCREEN_HEIGHT-300), f"{i+1}", fill=(60, 60, 60))
    
    # 비상등 (더 사실적)
    for i in range(2):
        x = 100 + i * (SCREEN_WIDTH-200)
        # 비상등 본체
        draw.rectangle([x-8, 40, x+8, 60], fill=(30, 0, 0))
        # 빛
        draw.ellipse([x-10, 50, x+10, 70], fill=(60, 0, 0))
    
    # 전체적으로 어둡게 조정
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.7)
    
    img.save('assets/corridor.jpg', quality=95)

def create_security():
    """보안실 - 고품질 모니터와 장비들"""
    img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), (8, 8, 8))
    draw = ImageDraw.Draw(img)
    
    # 바닥 (카펫 텍스처)
    carpet_noise = create_noise_texture(SCREEN_WIDTH, 100, 3)
    carpet_overlay = Image.new('RGB', (SCREEN_WIDTH, 100), (12, 12, 12))
    carpet_overlay = Image.blend(carpet_overlay, carpet_noise, 0.4)
    img.paste(carpet_overlay, (0, SCREEN_HEIGHT-100))
    
    # 벽 (어두운 패널)
    wall_noise = create_noise_texture(SCREEN_WIDTH, SCREEN_HEIGHT-100, 1)
    wall_overlay = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT-100), (6, 6, 6))
    wall_overlay = Image.blend(wall_overlay, wall_noise, 0.1)
    img.paste(wall_overlay, (0, 0))
    
    # 모니터들 (더 사실적)
    for i in range(3):
        for j in range(2):
            x = 150 + i * 300
            y = 100 + j * 250
            
            # 모니터 스탠드
            draw.rectangle([x+80, y+140, x+120, y+160], fill=(20, 20, 20))
            
            # 모니터 본체
            draw.rectangle([x, y, x+200, y+140], fill=(15, 15, 15))
            
            # 모니터 화면 (꺼진 상태)
            screen_noise = create_noise_texture(180, 120, 0.5)
            screen_overlay = Image.new('RGB', (180, 120), (3, 3, 3))
            screen_overlay = Image.blend(screen_overlay, screen_noise, 0.3)
            img.paste(screen_overlay, (x+10, y+10))
            
            # 모니터 프레임
            draw.rectangle([x, y, x+200, y+140], fill=None, outline=(25, 25, 25), width=3)
    
    # 영상기록 장치 (테이프 리코더)
    recorder_x = SCREEN_WIDTH//2
    recorder_y = SCREEN_HEIGHT - 200
    
    # 리코더 본체
    draw.rectangle([recorder_x-120, recorder_y-60, recorder_x+120, recorder_y+60], fill=(20, 20, 20))
    
    # 리코더 패널
    draw.rectangle([recorder_x-110, recorder_y-50, recorder_x+110, recorder_y+50], fill=(15, 15, 15))
    
    # 테이프 슬롯
    draw.rectangle([recorder_x-100, recorder_y-30, recorder_x-20, recorder_y+30], fill=(5, 5, 5))
    
    # 버튼들
    for i in range(5):
        btn_x = recorder_x - 80 + i * 30
        draw.ellipse([btn_x-8, recorder_y-10, btn_x+8, recorder_y+10], fill=(30, 30, 30))
    
    # 전선들 (더 자연스럽게)
    for i in range(6):
        x = 80 + i * 200
        # 전선 본체
        draw.line([(x, 50), (x, SCREEN_HEIGHT-120)], fill=(25, 25, 25), width=4)
        # 전선 커넥터
        draw.ellipse([x-5, SCREEN_HEIGHT-130, x+5, SCREEN_HEIGHT-120], fill=(35, 35, 35))
    
    # 전체적으로 어둡게 조정
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.5)
    
    img.save('assets/security.jpg', quality=95)

def create_ward():
    """병동 병실 - 고품질 병상과 커튼"""
    img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), (12, 12, 12))
    draw = ImageDraw.Draw(img)
    
    # 바닥 (병원 바닥 타일)
    tile_size = 50
    for x in range(0, SCREEN_WIDTH, tile_size):
        for y in range(SCREEN_HEIGHT-100, SCREEN_HEIGHT, tile_size):
            color = (15, 15, 15) if (x + y) % (tile_size * 2) == 0 else (10, 10, 10)
            draw.rectangle([x, y, x+tile_size, y+tile_size], fill=color)
    
    # 벽 (병원 벽 텍스처)
    wall_noise = create_noise_texture(SCREEN_WIDTH, SCREEN_HEIGHT-100, 1)
    wall_overlay = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT-100), (10, 10, 10))
    wall_overlay = Image.blend(wall_overlay, wall_noise, 0.15)
    img.paste(wall_overlay, (0, 0))
    
    # 병상들 (더 상세하게)
    for i in range(3):
        x = 150 + i * 300
        y = SCREEN_HEIGHT - 280
        
        # 병상 프레임
        draw.rectangle([x, y, x+220, y+100], fill=(18, 18, 18))
        
        # 병상 매트리스
        draw.rectangle([x+10, y+10, x+210, y+90], fill=(25, 25, 25))
        
        # 병상 시트 (주름 효과)
        for j in range(5):
            wrinkle_y = y + 15 + j * 15
            draw.line([(x+15, wrinkle_y), (x+205, wrinkle_y)], fill=(22, 22, 22), width=1)
        
        # 베개
        draw.rectangle([x+20, y+20, x+80, y+50], fill=(20, 20, 20))
        
        # 병상 레일
        draw.rectangle([x, y+40, x+220, y+45], fill=(15, 15, 15))
    
    # 커튼들 (더 자연스럽게)
    for i in range(3):
        x = 150 + i * 300
        
        # 커튼 폴
        draw.rectangle([x+100, 50, x+120, SCREEN_HEIGHT-280], fill=(35, 35, 35))
        
        # 커튼 천 (주름 효과)
        curtain_width = 80
        for j in range(8):
            fold_x = x + 120 + j * 10
            draw.rectangle([fold_x, 60, fold_x+8, SCREEN_HEIGHT-290], fill=(30, 30, 30))
            draw.rectangle([fold_x+1, 60, fold_x+7, SCREEN_HEIGHT-290], fill=(25, 25, 25))
    
    # 창문 (어두운 밖)
    window_x = SCREEN_WIDTH - 200
    draw.rectangle([window_x, 100, window_x+180, SCREEN_HEIGHT-200], fill=(3, 3, 3))
    
    # 창문 프레임
    draw.rectangle([window_x, 100, window_x+180, SCREEN_HEIGHT-200], fill=None, outline=(20, 20, 20), width=3)
    
    # 의료 장비들
    for i in range(2):
        x = 100 + i * (SCREEN_WIDTH-200)
        y = SCREEN_HEIGHT - 150
        
        # 장비 본체
        draw.rectangle([x, y, x+100, y+60], fill=(18, 18, 18))
        
        # 장비 패널
        draw.rectangle([x+10, y+10, x+90, y+50], fill=(12, 12, 12))
        
        # 버튼들
        for j in range(3):
            btn_x = x + 20 + j * 20
            draw.ellipse([btn_x-3, y+20, btn_x+3, y+26], fill=(25, 25, 25))
    
    # 전체적으로 어둡게 조정
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.6)
    
    img.save('assets/ward.jpg', quality=95)

def create_operating():
    """수술실 - 고품질 수술실 장비들"""
    img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), (5, 5, 5))
    draw = ImageDraw.Draw(img)
    
    # 바닥 (수술실 바닥)
    floor_noise = create_noise_texture(SCREEN_WIDTH, 100, 2)
    floor_overlay = Image.new('RGB', (SCREEN_WIDTH, 100), (12, 12, 12))
    floor_overlay = Image.blend(floor_overlay, floor_noise, 0.3)
    img.paste(floor_overlay, (0, SCREEN_HEIGHT-100))
    
    # 벽 (수술실 벽)
    wall_noise = create_noise_texture(SCREEN_WIDTH, SCREEN_HEIGHT-100, 1)
    wall_overlay = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT-100), (4, 4, 4))
    wall_overlay = Image.blend(wall_overlay, wall_noise, 0.1)
    img.paste(wall_overlay, (0, 0))
    
    # 수술대 (중앙)
    table_x = SCREEN_WIDTH//2
    table_y = SCREEN_HEIGHT - 320
    
    # 수술대 프레임
    draw.rectangle([table_x-180, table_y, table_x+180, table_y+100], fill=(20, 20, 20))
    
    # 수술대 상판
    draw.rectangle([table_x-170, table_y, table_x+170, table_y+90], fill=(25, 25, 25))
    
    # 수술대 다리들
    for i in range(4):
        leg_x = table_x - 150 + i * 100
        draw.rectangle([leg_x, table_y+90, leg_x+20, table_y+100], fill=(15, 15, 15))
    
    # 작업등들 (더 사실적)
    for i in range(3):
        x = 200 + i * 300
        y = 80
        
        # 등 프레임
        draw.rectangle([x-25, y, x+25, y+50], fill=(25, 25, 25))
        
        # 등 본체
        draw.ellipse([x-20, y+10, x+20, y+40], fill=(20, 20, 20))
        
        # 빛 (더 자연스럽게)
        for j in range(5):
            radius = j * 12
            alpha = 60 - j * 10
            if alpha > 0:
                light_overlay = Image.new('RGBA', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 0))
                light_draw = ImageDraw.Draw(light_overlay)
                light_draw.ellipse([x-radius, y+40-radius, x+radius, y+40+radius], fill=(60, 60, 20, alpha))
                img = Image.alpha_composite(img.convert('RGBA'), light_overlay).convert('RGB')
    
    # 수술 도구들
    tools_x = SCREEN_WIDTH//2
    tools_y = SCREEN_HEIGHT - 220
    
    # 도구함
    draw.rectangle([tools_x-120, tools_y, tools_x+120, tools_y+80], fill=(18, 18, 18))
    
    # 도구함 상판
    draw.rectangle([tools_x-110, tools_y, tools_x+110, tools_y+70], fill=(15, 15, 15))
    
    # 도구들 (간단한 표현)
    for i in range(8):
        tool_x = tools_x - 100 + i * 25
        draw.rectangle([tool_x, tools_y+10, tool_x+3, tools_y+60], fill=(30, 30, 30))
    
    # 바닥 얼룩 (혈흔)
    for i in range(4):
        x = 300 + i * 200
        y = SCREEN_HEIGHT - 130
        
        # 혈흔 본체
        draw.ellipse([x-25, y-15, x+25, y+15], fill=(25, 8, 8))
        
        # 혈흔 가장자리 (더 어둡게)
        draw.ellipse([x-30, y-20, x+30, y+20], fill=(15, 5, 5))
    
    # 모니터들
    for i in range(2):
        x = 100 + i * (SCREEN_WIDTH-200)
        y = 150
        
        # 모니터 스탠드
        draw.rectangle([x+60, y+80, x+80, y+100], fill=(20, 20, 20))
        
        # 모니터
        draw.rectangle([x, y, x+140, y+80], fill=(8, 8, 8))
        
        # 모니터 화면
        draw.rectangle([x+5, y+5, x+135, y+75], fill=(3, 3, 3))
    
    # 전체적으로 어둡게 조정
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.4)
    
    img.save('assets/operating.jpg', quality=95)

def create_stairs():
    """계단실 - 고품질 내려가는 계단"""
    img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), (15, 15, 15))
    draw = ImageDraw.Draw(img)
    
    # 벽 (계단실 벽)
    wall_noise = create_noise_texture(SCREEN_WIDTH, SCREEN_HEIGHT, 1)
    wall_overlay = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), (12, 12, 12))
    wall_overlay = Image.blend(wall_overlay, wall_noise, 0.1)
    img.paste(wall_overlay, (0, 0))
    
    # 계단들 (더 사실적)
    stair_width = 400
    stair_height = 45
    start_x = SCREEN_WIDTH//2 - stair_width//2
    start_y = 80
    
    for i in range(10):
        y = start_y + i * stair_height
        x = start_x + i * 25  # 계단이 아래로 갈수록 넓어짐
        width = stair_width + i * 50
        
        # 계단 상판
        draw.rectangle([x, y, x+width, y+stair_height], fill=(20, 20, 20))
        
        # 계단 가장자리
        draw.rectangle([x, y, x+width, y+8], fill=(30, 30, 30))
        
        # 계단 측면
        draw.rectangle([x, y+stair_height, x+width, y+stair_height+15], fill=(18, 18, 18))
    
    # 안내도 (벽에)
    sign_x = 100
    sign_y = 120
    
    # 안내도 프레임
    draw.rectangle([sign_x, sign_y, sign_x+250, sign_y+120], fill=(25, 25, 25))
    
    # 안내도 배경
    draw.rectangle([sign_x+10, sign_y+10, sign_x+240, sign_y+110], fill=(20, 20, 20))
    
    # 글씨 (볼펜으로 쓴 듯)
    draw.text((sign_x+30, sign_y+30), "지하=돌아오지 마", fill=(80, 80, 80))
    draw.text((sign_x+30, sign_y+60), "경고: 출입금지", fill=(100, 50, 50))
    
    # 비상등 (더 사실적)
    for i in range(2):
        x = 100 + i * (SCREEN_WIDTH-200)
        
        # 비상등 본체
        draw.rectangle([x-10, 40, x+10, 60], fill=(30, 0, 0))
        
        # 빛
        draw.ellipse([x-12, 50, x+12, 70], fill=(60, 0, 0))
    
    # 어둠 효과 (아래쪽이 더 어두움)
    dark_overlay = Image.new('RGBA', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 0))
    dark_draw = ImageDraw.Draw(dark_overlay)
    
    for i in range(8):
        y = SCREEN_HEIGHT - 200 + i * 25
        alpha = 30 + i * 8
        dark_draw.rectangle([0, y, SCREEN_WIDTH, y+25], fill=(0, 0, 0, alpha))
    
    img = Image.alpha_composite(img.convert('RGBA'), dark_overlay).convert('RGB')
    
    # 전체적으로 어둡게 조정
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.6)
    
    img.save('assets/stairs.jpg', quality=95)

def create_morgue():
    """시체안치실 - 고품질 서랍과 이름표"""
    img = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), (3, 3, 3))
    draw = ImageDraw.Draw(img)
    
    # 바닥 (시체안치실 바닥)
    floor_noise = create_noise_texture(SCREEN_WIDTH, 100, 2)
    floor_overlay = Image.new('RGB', (SCREEN_WIDTH, 100), (8, 8, 8))
    floor_overlay = Image.blend(floor_overlay, floor_noise, 0.4)
    img.paste(floor_overlay, (0, SCREEN_HEIGHT-100))
    
    # 벽 (시체안치실 벽)
    wall_noise = create_noise_texture(SCREEN_WIDTH, SCREEN_HEIGHT-100, 1)
    wall_overlay = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT-100), (2, 2, 2))
    wall_overlay = Image.blend(wall_overlay, wall_noise, 0.05)
    img.paste(wall_overlay, (0, 0))
    
    # 서랍들 (시체 보관용)
    for i in range(4):
        x = 200 + i * 220
        y = SCREEN_HEIGHT - 320
        
        # 서랍 프레임
        draw.rectangle([x, y, x+180, y+220], fill=(15, 15, 15))
        
        # 서랍 본체
        if i == 1:  # 두 번째 서랍이 열려있음
            # 열린 서랍
            draw.rectangle([x+10, y+10, x+170, y+210], fill=(8, 8, 8))
            # 서랍 내부 (어둡게)
            draw.rectangle([x+10, y+10, x+90, y+210], fill=(5, 5, 5))
        else:
            # 닫힌 서랍
            draw.rectangle([x+10, y+10, x+170, y+210], fill=(12, 12, 12))
        
        # 서랍 손잡이
        handle_x = x + 160
        handle_y = y + 110
        draw.ellipse([handle_x-8, handle_y-8, handle_x+8, handle_y+8], fill=(25, 25, 25))
    
    # 이름표들 (떨리는 듯)
    for i in range(4):
        x = 200 + i * 220
        y = SCREEN_HEIGHT - 340
        
        # 이름표 프레임
        draw.rectangle([x+60, y, x+120, y+25], fill=(20, 20, 20))
        
        # 이름표 배경
        draw.rectangle([x+62, y+2, x+118, y+23], fill=(15, 15, 15))
        
        # 이름 (흔들리는 효과)
        offset = (i % 2) * 3
        draw.text((x+70+offset, y+5), f"환자 {i+1}", fill=(60, 60, 60))
    
    # 차가운 공기 효과 (안개)
    fog = Image.new('RGBA', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 0))
    fog_draw = ImageDraw.Draw(fog)
    
    for i in range(20):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(100, SCREEN_HEIGHT-200)
        size = random.randint(80, 200)
        alpha = random.randint(10, 30)
        fog_draw.ellipse([x-size//2, y-size//4, x+size//2, y+size//4], fill=(150, 150, 150, alpha))
    
    img = Image.alpha_composite(img.convert('RGBA'), fog).convert('RGB')
    
    # 어둠 효과
    dark_overlay = Image.new('RGBA', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 120))
    img = Image.alpha_composite(img.convert('RGBA'), dark_overlay).convert('RGB')
    
    # 전체적으로 어둡게 조정
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.3)
    
    img.save('assets/morgue.jpg', quality=95)

if __name__ == "__main__":
    print("고품질 배경 이미지들을 생성하고 있습니다...")
    
    create_exterior()
    print("✓ exterior.jpg 생성 완료")
    
    create_lobby()
    print("✓ lobby.jpg 생성 완료")
    
    create_corridor()
    print("✓ corridor.jpg 생성 완료")
    
    create_security()
    print("✓ security.jpg 생성 완료")
    
    create_ward()
    print("✓ ward.jpg 생성 완료")
    
    create_operating()
    print("✓ operating.jpg 생성 완료")
    
    create_stairs()
    print("✓ stairs.jpg 생성 완료")
    
    create_morgue()
    print("✓ morgue.jpg 생성 완료")
    
    print("\n모든 고품질 배경 이미지가 assets 폴더에 생성되었습니다!")
    print("이제 게임을 실행하면 더 사실적이고 공포 분위기의 배경 이미지가 표시됩니다.")
