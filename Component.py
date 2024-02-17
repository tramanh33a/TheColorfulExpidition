class Button:
    def __init__(self,x,y,w,h,font,content,bg,func, arg):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.font = font
        self.content = content
        self.bg = bg
        self.func = func
        self.arg = arg

    def inRange(self,m):
        return (m[0] >= self.x and m[0] <= self.x + self.w and m[1] >= self.y and m[1] <= self.y + self.h)

    def blit(self,screen):
        screen.blit( self.bg, (self.x, self.y) )
        if not self.content == "":
            Text = self.font.render(self.content, True, (0,0,0))
            screen.blit( Text ,(self.x + (self.w - Text.get_width() ) / 2, self.y + (self.h - Text.get_height()) / 2) )
