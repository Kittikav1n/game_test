import pygame
import sys
import random

# --- ค่าคงที่ ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_FELT = (0, 80, 50)
DARK_GREEN_FELT = (0, 60, 30)
RED_CARD = (200, 0, 0)
BUTTON_COLOR = (240, 240, 240)
BUTTON_HOVER_COLOR = (255, 255, 255)
BUTTON_SHADOW_COLOR = (50, 50, 50)
TEXT_COLOR = (30, 30, 30)
WIN_COLOR = (76, 175, 80)
LOSE_COLOR = (244, 67, 54)
TIE_COLOR = (255, 193, 7)


BET_AMOUNT = 100 # เงินเดิมพันต่อรอบ

# Card constants
CARD_WIDTH = 70
CARD_HEIGHT = 100
CARD_CORNER_RADIUS = 8

# --- ตั้งค่า Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("เกมป๊อกเด้ง0.1")

# Fonts
try:
    # Use a more modern-looking system font if available
    FONT_MAIN = pygame.font.SysFont("calibri", 28, bold=True)
    FONT_SMALL = pygame.font.SysFont("calibri", 22)
    FONT_CARD = pygame.font.SysFont("segoeuisymbol", 30)
    FONT_RESULT = pygame.font.SysFont("calibri", 48, bold=True)
except:
    FONT_MAIN = pygame.font.Font(None, 36)
    FONT_SMALL = pygame.font.Font(None, 28)
    FONT_CARD = pygame.font.Font(None, 40)
    FONT_RESULT = pygame.font.Font(None, 60)


# --- ตัวแปรควบคุมสถานะเกม ---
game_state = "player_turn"
round_over = False
deck, players = [], []
player_positions = [
    (SCREEN_WIDTH / 2, SCREEN_HEIGHT - CARD_HEIGHT), # Player 1 (User)
    (SCREEN_WIDTH / 2, CARD_HEIGHT / 2 + 10), # Player 2 (Dealer/Bot 1)
    (CARD_WIDTH, SCREEN_HEIGHT / 2), # Player 3 (Bot 2)
    (SCREEN_WIDTH - CARD_WIDTH * 2, SCREEN_HEIGHT / 2), # Player 4 (Bot 3)
]


# --- ฟังก์ชันของเกม (Core Logic - Unchanged) ---
def get_card_value(card):
    rank = card[1]
    if rank in ['J', 'Q', 'K', '10']: return 0
    elif rank == 'A': return 1
    else: return int(rank)

def calculate_hand_score(hand):
    return sum(get_card_value(card) for card in hand) % 10

def is_pok(hand, score):
    return len(hand) == 2 and score in [8, 9]

def determine_winner(player, dealer):
    player_pok = is_pok(player['hand'], player['score'])
    dealer_pok = is_pok(dealer['hand'], dealer['score'])

    if player_pok and not dealer_pok: return "win"
    if not player_pok and dealer_pok: return "lose"
    if player_pok and dealer_pok:
        if player['score'] > dealer['score']: return "win"
        if player['score'] < dealer['score']: return "lose"
        return "tie"
    
    # กรณีไม่มีใครป๊อก
    if player['score'] > dealer['score']: return "win"
    if player['score'] < dealer['score']: return "lose"
    return "tie"

def setup_new_round():
    global deck, players, game_state, round_over
    
    old_chips = []
    if players:
        old_chips = [p['chips'] for p in players]

    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [(s, r) for s in suits for r in ranks]
    random.shuffle(deck)

    players = []
    for i in range(4):
        initial_chips = old_chips[i] if old_chips else 1000
        players.append({
            "name": f"Bot {i}" if i != 0 else "ผู้เล่น",
            "hand": [], 
            "chips": initial_chips,
            "score": 0, "status": "", "action": "pending", "result": ""
        })
    
    for _ in range(2):
        for player in players:
            if deck: player["hand"].append(deck.pop())

    for player in players:
        player['score'] = calculate_hand_score(player['hand'])
        if is_pok(player['hand'], player['score']):
            player['status'] = f"ป๊อก {player['score']}!"
            player['action'] = "stay"

    if any(p['status'] != "" for p in players):
        game_state = 'scoring'
    else:
        game_state = "player_turn"
        
    round_over = False

# --- ฟังก์ชันสำหรับวาด (Drawing Functions) ---
def draw_rounded_rect(surface, rect, color, corner_radius):
    pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

def draw_table():
    screen.fill(DARK_GREEN_FELT)
    table_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
    pygame.draw.ellipse(screen, GREEN_FELT, table_rect)
    pygame.draw.ellipse(screen, BLACK, table_rect, 4)

def draw_card(surface, card_tuple, x, y):
    card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    draw_rounded_rect(surface, card_rect, WHITE, CARD_CORNER_RADIUS)
    pygame.draw.rect(surface, BLACK, card_rect, 2, border_radius=CARD_CORNER_RADIUS)

    suit, rank = card_tuple
    suit_symbols = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
    color = RED_CARD if suit in ['Hearts', 'Diamonds'] else BLACK
    
    rank_surf = FONT_MAIN.render(rank, True, color)
    suit_surf = FONT_CARD.render(suit_symbols[suit], True, color)

    surface.blit(rank_surf, (x + 8, y + 5))
    surface.blit(suit_surf, (x + 8, y + 35))

def draw_button(surface, text, rect, mouse_pos, is_clicked):
    is_hover = rect.collidepoint(mouse_pos)
    
    shadow_rect = rect.copy()
    shadow_rect.y += 4
    draw_rounded_rect(surface, shadow_rect, BUTTON_SHADOW_COLOR, 12)

    button_rect = rect.copy()
    if is_hover and is_clicked:
        button_rect.y += 2

    bg_color = BUTTON_HOVER_COLOR if is_hover else BUTTON_COLOR
    draw_rounded_rect(surface, button_rect, bg_color, 12)
    pygame.draw.rect(surface, BLACK, button_rect, 2, 12)

    text_surf = FONT_MAIN.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=button_rect.center)
    surface.blit(text_surf, text_rect)

def draw_round_end_overlay():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

# --- เริ่มต้นรอบแรก ---
setup_new_round()

# --- Game Loop ---
running = True
clock = pygame.time.Clock()
while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    # --- จัดการ Event ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True
            
    # --- ตรรกะของเกม ---
    stay_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 140, SCREEN_HEIGHT - 70, 120, 50)
    hit_button_rect = pygame.Rect(SCREEN_WIDTH / 2 + 20, SCREEN_HEIGHT - 70, 120, 50)
    next_round_rect = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 60, 200, 60)

    if game_state == 'player_turn' and not round_over:
        if mouse_clicked:
            if stay_button_rect.collidepoint(mouse_pos):
                players[0]['action'] = 'stay'
                game_state = 'bots_turn'
            elif hit_button_rect.collidepoint(mouse_pos):
                players[0]['action'] = 'hit'
                if deck:
                    players[0]['hand'].append(deck.pop())
                    players[0]['score'] = calculate_hand_score(players[0]['hand'])
                game_state = 'bots_turn'

    if game_state == 'bots_turn':
        for i in range(1, 4):
            if players[i]['action'] == 'pending':
                players[i]['action'] = 'hit' if players[i]['score'] < 4 else 'stay'
                if players[i]['action'] == 'hit' and deck:
                    players[i]['hand'].append(deck.pop())
                    players[i]['score'] = calculate_hand_score(players[i]['hand'])
        game_state = 'scoring'

    if game_state == 'scoring' and not round_over:
        dealer = players[1] 
        dealer['name'] = "เจ้ามือ (Bot 1)"
        
        for i in range(4):
            if i == 1: continue 
            
            player = players[i]
            result = determine_winner(player, dealer)
            player['result'] = result
            
            if result == "win":
                player['chips'] += BET_AMOUNT
                dealer['chips'] -= BET_AMOUNT
            elif result == "lose":
                player['chips'] -= BET_AMOUNT
                dealer['chips'] += BET_AMOUNT
        
        round_over = True
        game_state = 'end_round'
        
    if game_state == 'end_round' and mouse_clicked:
        if next_round_rect.collidepoint(mouse_pos):
            setup_new_round()

    # --- การวาดภาพ ---
    draw_table()
    
    # Draw players and cards
    for i, player in enumerate(players):
        pos_x, pos_y = player_positions[i]
        num_cards = len(player['hand'])
        start_x = pos_x - (num_cards * (CARD_WIDTH + 5) - 5) / 2

        # Info text position
        info_y = pos_y + CARD_HEIGHT + 10 if i == 1 else pos_y - 65

        info_text = f"{player['name']} - เงิน: {player['chips']}"
        info_surf = FONT_MAIN.render(info_text, True, WHITE)
        info_rect = info_surf.get_rect(center=(pos_x, info_y))
        screen.blit(info_surf, info_rect)
        
        status_text = f"คะแนน: {player['score']} {player['status']}"
        status_surf = FONT_SMALL.render(status_text, True, WHITE)
        status_rect = status_surf.get_rect(center=(pos_x, info_y + 30))
        screen.blit(status_surf, status_rect)

        for j, card in enumerate(player['hand']):
            draw_card(screen, card, start_x + j * (CARD_WIDTH + 5), pos_y)
        
        # Draw result text
        if round_over and player['result']:
            result_map = {"win": ("ชนะ", WIN_COLOR), "lose": ("แพ้", LOSE_COLOR), "tie": ("เสมอ", TIE_COLOR)}
            text, color = result_map.get(player['result'], ("", WHITE))
            result_surf = FONT_RESULT.render(text, True, color)
            result_rect = result_surf.get_rect(center=(pos_x, pos_y + CARD_HEIGHT/2))
            screen.blit(result_surf, result_rect)

    if round_over:
        draw_round_end_overlay()
        draw_button(screen, "รอบต่อไป", next_round_rect, mouse_pos, mouse_clicked)
    elif game_state == 'player_turn':
        draw_button(screen, "อยู่ B ", stay_button_rect, mouse_pos, mouse_clicked)
        draw_button(screen, "จั่ว A ", hit_button_rect, mouse_pos, mouse_clicked)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
