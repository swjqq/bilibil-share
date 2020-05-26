from turtle import *
#设置画板大小
wight = 900
height = 1000
setup(wight,height)

#绘制速率
speed(10)
#取消画布的延迟
#Turtle().screen.delay(1)

#绘制网格
for i in range(17):
    up()
    goto(0+i*50-wight/2+50,0-height/2+50)
    down()
    seth(90)
    forward(1000)
for i in range(20):
    up()
    goto(0-wight/2+50,0+i*50-height/2+50)
    down()
    seth(0)
    forward(800)
#颜色设置
branch_color = "#E66129"    #树枝
leaf_color = "#BD4416"      #树叶
head_color = "#5F2C89"      #头
face_color = "#B292C3"      #脸
mouth_color = "#F7BB61"     #嘴巴
eye_color1 = "#FFFFFF"      #眼睛
eye_color2 = "#000000"      #眼球
eyelid_color = "#CBB6D7"    #眼帘
feather_color1 = "#CCB3D3"  #胸脯
feather_color2 = "#9377A7"  #羽毛
foot_color = "#5E4133"      #脚
sign_color = ("#8CCDED")    #签名


#树枝
width(10)
color(branch_color)
fillcolor(branch_color)
up()
goto(-170,-50)
down()
seth(-15)
for i in range(400):
    left(0.1)
    forward(1)

#树叶
leaf_fillcolor = "#00FF40"
color(leaf_color)
##下面叶子
seth(5)
width(3)
begin_fill()
fillcolor(leaf_fillcolor)
for i in range(2):
    for j in range(1,61):
        forward(3)
        right(2)
    right(60)
end_fill()
##树叶中间的线
seth(-83)
for i in range(190):
    left(0.3)
    forward(0.8)
##上面叶子
up()
goto(220,-10)
down()
begin_fill()
fillcolor(leaf_fillcolor)
seth(130)
for i in range(2):
    for j in range(1,61):
        forward(3)
        right(2)
    right(60)
end_fill()
##树叶中间的线
seth(100)
for i in range(190):
    right(0.3)
    forward(0.8)

#头
width(10)
up()
goto(0,0)
down()
seth(0)
color(head_color)
begin_fill()
fillcolor(head_color)
circle(200)
end_fill()

#脸
##左边直线
begin_fill()
color(face_color)
fillcolor(face_color)
up()
goto(-150,70)
down()
width(3)
color(face_color)
seth(90)
forward(265)
right(25)
forward(170)
right(120)
forward(137)
seth(270)
forward(303)
goto(-150,70)
end_fill()
##右边直线
begin_fill()
color(face_color)
fillcolor(face_color)
up()
goto(150,70)
down()
width(3)
seth(90)
forward(265)
left(25)
forward(170)
left(120)
forward(137)
seth(270)
forward(303)
goto(150,70)
end_fill()

#嘴巴
up()
goto(30,260)
down()
begin_fill()
color(mouth_color)
fillcolor(mouth_color)
seth(0)
#left(4)
width(3)
for i in range(3):
    right(120)
    forward(60)
end_fill()

#眼睛
up()
goto(-60,250)
down()
begin_fill()
color(eye_color1)
fillcolor(eye_color1)
seth(0)
width(3)
circle(60)
up()
goto(60,250)
down()
circle(60)
end_fill()
#眼珠
up()
goto(45,300)
down()
begin_fill()
color(eye_color2)
fillcolor(eye_color2)
circle(15)
up()
goto(-45,300)
down()
circle(15)
end_fill()

#眼皮
width(8)
##左边
up()
goto(-115,290)
down()
begin_fill()
color(eyelid_color)
fillcolor(eyelid_color)
left(35)
forward(111)
seth(138)
circle(60,154)
end_fill()
##右边
begin_fill()
up()
goto(115,290)
down()
seth(180)
right(35)
forward(111)
seth(44)
circle(-60,154)
end_fill()

#胸部
#胸脯
##左边圆弧
width(10)
begin_fill()
color(feather_color1)
fillcolor(feather_color1)
up()
goto(0,0)
down()
seth(180)
circle(-200,47.5)
seth(0)
forward(153)
goto(0,0)
##右边圆弧
width(10)
seth(0)
circle(200,47.5)
seth(180)
forward(153)
goto(0,0)
end_fill()
##上面圆弧
width(3)
begin_fill()
color(feather_color1)
fillcolor(feather_color1)
up()
goto(-150,70)
down()
seth(85)
circle(-150,170)
end_fill()
##羽毛
width(2)
color(feather_color2)
fillcolor(feather_color2)
for i in range(3):
    up()
    goto(-80 - i*20,170 - i*35)
    down()
    for j in range(4):
        if j < 2: 
            seth(260)
            circle(20 + i*5, 180)
        else:
            seth(280)
            circle(20 + i*5, 180)


#脚
color(foot_color)
##左脚
up()
goto(-60,10)
down()
seth(270)
width(10)
forward(50)
seth(-150)
forward(80)
up()
goto(-60,-40)
down()
seth(-120)
forward(85)
up()
goto(-60,-40)
down()
seth(-55)
forward(78)
##右脚
up()
goto(60,10)
down()
seth(270)
width(10)
forward(50)
seth(-130)
forward(80)
up()
goto(60,-40)
down()
seth(-75)
forward(85)
up()
goto(60,-40)
down()
seth(-40)
forward(78)

#签名
up()
goto(-300,-250)
color(sign_color)
write("十万九千七",font=("微软雅黑",30))
goto(-280,-300)
write("2020年1月1日",font=("微软雅黑",30))

#隐藏海龟并结束
hideturtle()
done()
