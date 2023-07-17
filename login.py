#login.py
import pygame
from pygame.locals import *
import http.client
import json


class LoginScreen:
    def __init__(self):
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Login Screen')
        self.WHITE = (255, 255, 255, 200)
        self.BLACK = (0, 0, 0)
        self.font = pygame.font.Font(None, 32)
        self.username = ''
        self.password = ''
        self.username_active = True
        self.password_active = False
        self.conn = http.client.HTTPConnection("127.0.0.1", 8001)
        self.headers = {
            "Accept": "*/*",
            "User-Agent": "Mortal Gold",
            "Content-Type": "application/json"
        }
        self.error_message = None


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    if self.is_username_active():
                        self.username = self.username[:-1]
                    elif self.is_password_active():
                        self.password = self.password[:-1]
                elif event.key == K_TAB:
                    self.toggle_username_active()
                    self.toggle_password_active()
                elif event.key == K_RETURN:
                    if self.username and self.password:
                        self.get_api_token()
                        self.match = self.join_create_match()
                        if self.username == self.match["player1"]:
                            self.match["current player"] = 0
                        else:
                            self.match["current player"] = 1
                        return self.match
                else:
                    if self.is_username_active() and len(self.username) < 25:
                        self.username += event.unicode
                    elif self.is_password_active() and len(self.password) < 30:
                        self.password += event.unicode
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # 1 represents the left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    if self.is_username_active() or self.is_password_active():
                        if self.login_button_rect.collidepoint(mouse_pos):
                            if self.username and self.password:
                                self.get_api_token()
                                self.match = self.join_create_match()
                                if self.username == self.match["player1"]:
                                    self.match["current player"] = 1
                                else:
                                    self.match["current player"] = 2
                                return self.match
                        elif self.cancel_button_rect.collidepoint(mouse_pos):
                            pygame.quit()

        return None


    def get_api_token(self):
        payload = json.dumps({
            "username": f"{self.username}",
            "password": f"{self.password}"
        })
        try:
            self.conn.request("POST", "/game/api-token-auth/", payload, self.headers)
            response = self.conn.getresponse()
            self.token = json.loads(response.read())
            print(self.token['token'])
            print(self.username)
            return self.username
        except Exception as e:
            print(e)
            self.error_message = 'Failed to get token. Please try again.'
            self.username = ''  
            self.password = ''
            return

    def join_create_match(self):
        self.header = {
        "Accept": "*/*",
        "User-Agent": "Mortal Gold",
        "Authorization": "Token " + self.token['token']
        }
        payload = ""
        try:
            self.conn.request("GET", "/game/match/", payload, self.header)
            response = self.conn.getresponse()
            match = json.loads(response.read())
            print(match)
            return match
        except Exception as e:
            print(e)
            self.error_message = 'Failed to connect. Please try again.'
            return


    def display(self):
        background = pygame.image.load('assets/images/background/bg.png')
        background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
        self.screen.blit(background, (0, 0))
        title_text = self.font.render('Login', True, self.WHITE)
        username_text = self.font.render('Username:', True, self.WHITE)
        password_text = self.font.render('Password:', True, self.WHITE)

        # Truncate the username to a maximum of 25 characters
        truncated_username = self.username[:25]

        username_input = self.font.render(truncated_username, True, self.WHITE)
        password_input = self.font.render('*' * len(self.password), True, self.WHITE)
        username_rect = pygame.Rect(200, 200, 400, 50)
        password_rect = pygame.Rect(200, 300, 400, 50)
        pygame.draw.rect(self.screen, self.WHITE, username_rect, 2)
        pygame.draw.rect(self.screen, self.WHITE, password_rect, 2)
        self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 100))
        self.screen.blit(username_text, (76, 211))
        self.screen.blit(password_text, (82, 312))

        # Adjust the X coordinate to center the text in the input boxes
        username_input_x = 210 + (380 - username_input.get_width()) // 2
        password_input_x = 210 + (380 - password_input.get_width()) // 2

        # Adjust the Y coordinate to center the text vertically
        username_input_y = 214
        password_input_y = 319

        self.screen.blit(username_input, (username_input_x, username_input_y))
        self.screen.blit(password_input, (password_input_x, password_input_y))

        self.login_button_rect = pygame.Rect(200, 400, 180, 50)
        self.cancel_button_rect = pygame.Rect(418, 400, 182, 50)
        pygame.draw.rect(self.screen, self.WHITE, self.login_button_rect, 2)
        pygame.draw.rect(self.screen, self.WHITE, self.cancel_button_rect, 2)
        login_button_text = self.font.render('Login', True, self.WHITE)
        cancel_button_text = self.font.render('Exit', True, self.WHITE)
        self.screen.blit(login_button_text, (258, 413))
        self.screen.blit(cancel_button_text, (487, 413))

        if self.error_message:
            error = self.font.render(self.error_message, True, self.WHITE)
            self.screen.blit(error, (600, 360))

        pygame.display.flip()

    def is_username_active(self):
        return self.username_active

    def is_password_active(self):
        return self.password_active

    def toggle_username_active(self):
        self.username_active = not self.is_username_active()

    def toggle_password_active(self):
        self.password_active = not self.is_password_active()

    def run(self):
        while True:
            result = self.handle_events()
            if result is not None:
                return result
            self.display()
