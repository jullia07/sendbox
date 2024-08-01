import pygame
import math    #삼각함수를 쓰기 위해 필요

class Ball(pygame.sprite.Sprite):
    #img 이미지
    def __init__(self,img,x,y):
        super().__init__()
        self.image = img
        self.rect = img.get_rect()
        self.rect.center = (x,y)
        self.mask = pygame.mask.from_surface(img) #충돌체크용 마스크 생성
        self.go = False #공을 움직일 거면 True, 기본값은 당연히 False
        self.dt = 2 #공의 이동 거리, 속도
        self.x = x  #공의 현재 x 좌표 
        self.y = y  #공의 현재 y 좌표 
        self.dirx = 1   
        self.diry = 1

    #공이 움직일 공간
    def boundRect(self,rect):
        self.brect = rect
    
    #주어진 각도로 공을 움직임    
    def start(self, angle):
        self.angle = angle
        self.go = True
    
    #공과 막대의 충돌시 공의 방향을 바꿈    
    def collideBar(self):
        self.diry *=-1

    def move(self,surface):        
        if not self.go : return #게임이 시작되지 않았으면 아래 내용을 실행하지 않고 리턴시킴
        
        #공의 이동을 계산 
        xd = math.sin(math.radians(self.angle)) * self.dt *self.dirx
        yd = math.cos(math.radians(self.angle)) * self.dt *self.diry
        #구해진 이동거리를 원래 좌표에 더해서 이동함
        self.x += xd
        self.y += yd
        
        #공이 벽에 맞고 튕기는 부분. brect 는 공이 이동 가능한 공간, rect는 공의 사각범위임
        # dirx 와 diry 에 -1 을 곱해 방향을 바꿔준다.
        if self.x - self.rect.width/2 < self.brect.x : 
            self.x = self.brect.x + self.rect.width/2
            self.dirx *= -1
        if self.y - self.rect.width/2 < self.brect.y :
            self.y = self.brect.y + self.rect.width/2
            self.diry *= -1
        if self.x + self.rect.width/2 > self.brect.x + self.brect.width :
            self.x = self.brect.x + self.brect.width - self.rect.width/2
            self.dirx *= -1
        if self.y + self.rect.width/2  > self.brect.y + self.brect.height:
            self.y = self.brect.y + self.brect.height - self.rect.width/2
            self.diry *= -1
        
        #공의 새로운 위치를 입력해주고
        self.rect.center = (self.x,self.y)
        #공을 그린다.
        surface.blit(self.image,self.rect)