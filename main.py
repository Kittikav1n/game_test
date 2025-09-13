import pygame
import sys
import random

# --- ค่าคงที่ ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE, BLACK, GREEN = (255, 255, 255), (0, 0, 0), (0, 50, 20)
YELLOW, CYAN = (255, 255, 0), (0, 255, 255)
BUTTON_COLOR, BUTTON_HOVER_COLOR = (70, 70, 70), (100, 100, 100)
BET_AMOUNT = 100 # เงินเดิมพันต่อรอบ

# --- ตั้งค่า Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pok Deng Prototype - Final")
font = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 28)

# --- ตัวแปรควบคุมสถานะเกม ---
game_state = "player_turn"
round_over = False
deck, players = [], []

# --- ฟังก์ชันของเกม ---
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
    
    # --- THIS IS THE FIX ---
    # 1. Save old chip counts before doing anything else.
    old_chips = []
    if players: # Check if this is not the first round
        old_chips = [p['chips'] for p in players]
    # --- END OF FIX ---

    deck = [(s, r) for s in ['Hearts', 'Diamonds', 'Clubs', 'Spades'] for r in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']]
    random.shuffle(deck)

    players = [] # Now it's safe to clear the list for the new round.
    for i in range(4):
        # Use the saved old_chips list to set the starting chips.
        initial_chips = old_chips[i] if old_chips else 1000
        players.append({
            "name": f"Bot {i}" if i != 0 else "Player 1", 
            "hand": [], 
            "chips": initial_chips,
            "score": 0, "status": "", "action": "pending", "result": ""
        })
    
    # (The rest of the function stays the same)
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
    
def draw_button(text, x, y, width, height, color, hover_color):
    mouse_pos = pygame.mouse.get_pos()
    is_hover = x < mouse_pos[0] < x + width and y < mouse_pos[1] < y + height
    
    btn_color = hover_color if is_hover else color
    pygame.draw.rect(screen, btn_color, (x, y, width, height))
    
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x + width / 2, y + height / 2))
    screen.blit(text_surf, text_rect)
    return is_hover

# --- เริ่มต้นรอบแรก ---
setup_new_round()

# --- Game Loop ---
running = True
while running:
    # --- จัดการ Event ---
    mouse_clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True
            
    # --- ตรรกะของเกม ---
    if game_state == 'player_turn' and mouse_clicked:
        if draw_button("AAAA", 550, 500, 100, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR):
            players[0]['action'] = 'stay'
            game_state = 'bots_turn'
        if draw_button("BBBB", 670, 500, 100, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR):
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
        dealer = players[1] # กำหนดให้ Bot 1 เป็นเจ้ามือ
        dealer['name'] = "Dealer (Bot 1)"
        
        for i in range(4):
            if i == 1: continue # ข้ามตัวเจ้ามือเอง
            
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
        if draw_button("รอบต่อไป", SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 50, 200, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR):
            # เก็บชิปเก่าไว้ แล้วเริ่มรอบใหม่
            old_chips = [p['chips'] for p in players]
            setup_new_round()
            for i in range(4):
                players[i]['chips'] = old_chips[i]


    # --- การวาดภาพ ---
    screen.fill(GREEN)
    y_position = 50
    for player in players:
        # แสดงชื่อและชิป
        info_text = f"{player['name']} - Chips: {player['chips']}"
        info_surface = font.render(info_text, True, WHITE)
        screen.blit(info_surface, (50, y_position))
        
        # แสดงไพ่
        hand_text = ' '.join([f'[{card[1]}{card[0][0]}]' for card in player['hand']])
        hand_surface = font.render(hand_text, True, YELLOW)
        screen.blit(hand_surface, (50, y_position + 40))
        
        # แสดงคะแนนและสถานะ
        status_text = f"Score: {player['score']} {player['status']}"
        status_surface = font_small.render(status_text, True, CYAN)
        screen.blit(status_surface, (50, y_position + 80))
        
        # แสดงผลลัพธ์ตอนจบรอบ
        if round_over and player['result']:
            result_color = (0,255,0) if player['result'] == 'win' else (255,0,0) if player['result'] == 'lose' else WHITE
            result_surface = font.render(player['result'].upper(), True, result_color)
            screen.blit(result_surface, (400, y_position + 5))
            
        y_position += 130

    if game_state == 'player_turn':
        draw_button("อยู่", 550, 500, 100, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        draw_button("จั่ว", 670, 500, 100, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)
    
    if round_over:
        draw_button("รอบต่อไป", SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 50, 200, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)

    pygame.display.flip()

pygame.quit()
sys.exit()