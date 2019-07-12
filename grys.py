import pygame
from PIL import Image,ImageDraw
import numpy
import sys
import os
import random
import matplotlib.pyplot as plt
import tensorflow as tf
import time
import math
import threading

def koloruj(x,y,image):
	p=image.getpixel((x,y))
	a=[p[0],p[1],p[2]]
	i=1
	'''if x>0:
		p=image.getpixel((x-1,y))
		a[0]+=p[0]/2
		a[1]+=p[1]/2
		a[2]+=p[2]/2
		i+=0.5
	if y>0:
		p=image.getpixel((x,y-1))
		a[0]+=p[0]/2
		a[1]+=p[1]/2
		a[2]+=p[2]/2
		i+=0.5'''
	if x<99:
		p=image.getpixel((x+1,y))
		a[0]+=p[0]/2
		a[1]+=p[1]/2
		a[2]+=p[2]/2
		i+=0.5
	if y<79:
		p=image.getpixel((x,y+1))
		a[0]+=p[0]/2
		a[1]+=p[1]/2
		a[2]+=p[2]/2
		i+=0.5
	a[0]/=i
	a[1]/=i
	a[2]/=i
	a[0]+=random.randint(0,50)-25
	a[1]+=random.randint(0,50)-25
	a[2]+=random.randint(0,50)-25
	if a[0]>255: a[0]=255
	if a[0]<0: a[0]=0
	if a[1]>255: a[1]=255
	if a[1]<0: a[1]=0
	if a[2]>255: a[2]=255
	if a[2]<0: a[2]=0
	image.putpixel((x,y),(int(a[0]),int(a[1]),int(a[2])))

def tloo(tlo):
	for i in range(random.randint(0,5),100,5):
		for j in range(random.randint(0,5),80,5):
			koloruj(i,j,tlo)
	
def start():							#main function
	os.chdir('zdj')
	thr=[]
	gracz=[500,400,pygame.Rect(500,400,40,70),0,True]
	score=[-1]
	klocki=[]
	timeee=[1]
	image=[Image.new('1',(1000,800))]
	thr.append(threading.Thread(target=ruch,args=(klocki,gracz,score,timeee),daemon=True))
	thr.append(threading.Thread(target=rozpoznawanie,args=(klocki,score,image,timeee),daemon=True))
	thr.append(threading.Thread(target=gra,args=(klocki,gracz,score,thr[0],thr[1],image,timeee)))
	
	thr[2].start()
	thr[1].start()
	thr[0].start()
	
def rozpoznawanie(klocki, score,image,timeee):
	x=tf.placeholder(tf.float32,[None,4096])
	y=tf.placeholder(tf.float32,[None, 6])
	im=tf.reshape(x,[-1,64,64,1])
	c1=tf.layers.conv2d(im,16,2,1,'same',activation=tf.nn.relu)
	p1=tf.layers.max_pooling2d(c1,2,2)
	c2=tf.layers.conv2d(p1,64,2,1,'same',activation=tf.nn.relu)
	p2=tf.layers.max_pooling2d(c2,2,2)
	flat=tf.layers.flatten(p2)
	l1=tf.layers.dense(flat, 128,tf.nn.relu)
	out=tf.layers.dense(l1,6,tf.nn.sigmoid)
	sess=tf.Session()
	saver = tf.train.Saver()
	saver.restore(sess, './grys')
	czy=True
	punkt=[0,0]
	imdraw=ImageDraw.Draw(image[0])
	score[0]=0
	klik=False
	while score[0]>=0:
		if not pygame.mouse.get_pressed()[0] and klik:
			klik=False
			lista=list(image[0].crop(image[0].getbbox()).resize((64,64)).getdata())
			for j in range(len(lista)):
				if lista[j]==255:
					lista[j]=1
			ou=sess.run(out,{x:[lista]})
			wynik=5
			for i in range(5):
				if ou[0][i]>ou[0][wynik]:
					wynik=i
			proc=0
			for i in range(5):
				proc+=ou[0][i]
			proc/=5
			if (ou[0][wynik]/proc)>0.8 and ou[0][wynik]>=0.5:
				ii=0
				while ii<len(klocki):
					if klocki[ii][0]==wynik:
						score[0]+=1
						timeee[0]-=0.005
						klocki.remove(klocki[ii])
					else:
						ii+=1
				
			
			image[0]=Image.new('1',(1000,800))
			imdraw=ImageDraw.Draw(image[0])
			czy=True
		if pygame.mouse.get_pressed()[0]:
			klik=True
			pos = pygame.mouse.get_pos()
			if czy:
				czy=False
				punkt[0]=pos[0]
				punkt[1]=pos[1]
			imdraw.line([(punkt[0],punkt[1]),(pos[0],pos[1])],1,5)
			punkt[0]=pos[0]
			punkt[1]=pos[1]
		time.sleep(0.0025)
	

def gra(klocki,gracz,score,thr,thrr,image,timeee):
	pygame.init()
	pygame.font.init()
	window = pygame.display.set_mode((1000, 800))
	pygame.display.set_caption(('Gra'))
	clock = pygame.time.Clock()
	liczba=0
	zdjj=[]
	for i in range(6):
		pp=Image.open('T'+str(i)+'.jpeg').resize((40,40)).convert('RGB')
		for j in range(40):
			for k in range(40):
				ppp=pp.getpixel((j,k))
				if ppp[0]<125 and ppp[1]<125 and ppp[2]<125:
					pp.putpixel((j,k),(0,0,0))
				else:
					pp.putpixel((j,k),(255,255,255))
		zdjj.append(pygame.image.frombuffer(pp.tobytes(),(40,40),'RGB'))
		zdjj[i].set_colorkey((0,0,0))
	postacie=[]
	postacie.append(pygame.image.load('gracz.jpg'))
	postacie.append(pygame.image.load('wrog.jpg'))
	timee=time.time()
	ttt=time.time()
	tlo=Image.new('RGB',(100,80),(random.randint(100,200),random.randint(100,200),random.randint(100,200)))
	tloo(tlo)
	font=pygame.font.Font(None,50)
	while score[0]==-1:
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				sys.exit(0)
		window.fill((0,0,0))
		if random.randint(0,20)==0:
			tloo(tlo)
		window.blit(pygame.image.frombuffer(tlo.resize((1000,800)).tobytes(),(1000,800),'RGB'),(0,0))
		window.blit(font.render("Ładowanie...",True,(255,255,255)),(400,400))
		pygame.display.flip()
		clock.tick(60)
	while True:
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				score[0]=-1
				thr.join()
				thrr.join()
				sys.exit(0)
			
		if time.time()-timee>=timeee[0]:
			if random.randint(0,1)==0:
				if random.randint(0,1)==0:
					klocki.append([random.randint(0,5),pygame.Rect(random.randint(0,1000),0,40,70),0,0,0,random.randint(0,1)])
				else:
					klocki.append([random.randint(0,5),pygame.Rect(random.randint(0,1000),800,40,70),0,0,0,random.randint(0,1)])
			else:
				if random.randint(0,1)==0:
					klocki.append([random.randint(0,5),pygame.Rect(0,random.randint(0,800),40,70),0,0,0,random.randint(0,1)])
				else:
					klocki.append([random.randint(0,5),pygame.Rect(1000,random.randint(0,800),40,70),0,0,0,random.randint(0,1)])
			klocki[-1][2]=klocki[-1][1].x
			klocki[-1][3]=klocki[-1][1].y
			timee=time.time()
				
				
		window.fill((0,0,0))
		if random.randint(0,20)==0:
			tloo(tlo)
		window.blit(pygame.image.frombuffer(tlo.resize((1000,800)).tobytes(),(1000,800),'RGB'),(0,0))
		for i in range(len(klocki)-1,-1,-1):
			try:
				temp=pygame.transform.rotate(postacie[1],klocki[i][4])
				temp.set_colorkey((0,0,0))
				window.blit(temp,klocki[i][1])
				window.blit(zdjj[klocki[i][0]],(klocki[i][1].x,klocki[i][1].y-45))
			except:
				break
		obraz=pygame.image.frombuffer(image[0].convert('RGB').tobytes(),(1000,800),'RGB')
		obraz.set_colorkey(0)
		temp=pygame.transform.rotate(postacie[0],gracz[3])
		temp.set_colorkey((0,1,2))
		
		window.blit(temp,gracz[2])
		window.blit(font.render(str(score[0]),True,(255,255,255)),(900,60))
		window.blit(obraz,(0,0))
		pygame.display.flip()
		clock.tick(60)
		
def ruch(klocki,gracz,score,timeee):
	while score[0]==-1:
		pass
	tim=time.time()
	while score[0]>=0:
		if time.time()-tim>=0.03:
			tim=time.time()
			
			if pygame.key.get_pressed()[pygame.K_w]:
				if pygame.key.get_pressed()[pygame.K_d]:
					gracz[0]+=math.sqrt(2)*2
					gracz[1]+=-math.sqrt(2)*2	
				elif pygame.key.get_pressed()[pygame.K_a]:
					gracz[0]+=-math.sqrt(2)*2
					gracz[1]+=-math.sqrt(2)*2
				else: gracz[1]+=-4
				gracz[2].x=int(gracz[0])
				gracz[2].y=int(gracz[1])
				if gracz[4]:
					gracz[3]+=4
					if gracz[3]>15:
						gracz[4]=False
				else:
					gracz[3]-=4
					if gracz[3]<-15:
						gracz[4]=True
			if pygame.key.get_pressed()[pygame.K_s]:
				if pygame.key.get_pressed()[pygame.K_d]:
					gracz[0]+=math.sqrt(2)*2
					gracz[1]+=math.sqrt(2)*2
				elif pygame.key.get_pressed()[pygame.K_a]:
					gracz[0]+=-math.sqrt(2)*2
					gracz[1]+=math.sqrt(2)*2
				else: gracz[1]+=4
				gracz[2].x=int(gracz[0])
				gracz[2].y=int(gracz[1])
				if gracz[4]:
					gracz[3]+=4
					if gracz[3]>15:
						gracz[4]=False
				else:
					gracz[3]-=4
					if gracz[3]<-15:
						gracz[4]=True
			if pygame.key.get_pressed()[pygame.K_d] and not pygame.key.get_pressed()[pygame.K_w] and not pygame.key.get_pressed()[pygame.K_s]:
				gracz[0]+=4
				gracz[2].x=int(gracz[0])
				gracz[2].y=int(gracz[1])
				if gracz[4]:
					gracz[3]+=4
					if gracz[3]>15:
						gracz[4]=False
				else:
					gracz[3]-=4
					if gracz[3]<-15:
						gracz[4]=True
			if pygame.key.get_pressed()[pygame.K_a] and not pygame.key.get_pressed()[pygame.K_w] and not pygame.key.get_pressed()[pygame.K_s]:
				gracz[0]+=-4
				gracz[2].x=int(gracz[0])
				gracz[2].y=int(gracz[1])
				if gracz[4]:
					gracz[3]+=4
					if gracz[3]>15:
						gracz[4]=False
				else:
					gracz[3]-=4
					if gracz[3]<-15:
						gracz[4]=True
			
			for i in range(len(klocki)):
				kat=math.atan2(gracz[2].centery-klocki[i][1].centery,gracz[2].centerx-klocki[i][1].centerx)
				klocki[i][2]+=math.cos(kat)*2
				klocki[i][3]+=math.sin(kat)*2
				klocki[i][1].x=int(klocki[i][2])
				klocki[i][1].y=int(klocki[i][3])
				if klocki[i][5]:
					klocki[i][4]+=3
					if klocki[i][4]>15:
						klocki[i][5]=False
				else:
					klocki[i][4]-=3
					if klocki[i][4]<-15:
						klocki[i][5]=True
				if klocki[i][1].colliderect(gracz[2]):
					print('Score: '+str(score))
					score[0]=0
					gracz[0]=500
					gracz[1]=400
					gracz[2].x=int(gracz[0])
					gracz[2].y=int(gracz[1])
					klocki.clear()
					timeee[0]=1
					break
		time.sleep(0.001)	
			
def model(znak,liczba):
	os.chdir('models')
	pygame.init()
	window = pygame.display.set_mode((1000, 800))
	pygame.display.set_caption(('Modele'))
	clock = pygame.time.Clock()
	image=Image.new('1',(1000,800))
	imdraw=ImageDraw.Draw(image)
	czy=True
	punkt=[0,0]
	while True:
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				sys.exit(0)
			if event.type == pygame.MOUSEBUTTONUP:
				image=image.crop(image.getbbox()).resize((64,64))
				image.save('zdj\\'+str(znak)+str(liczba)+'.jpeg')
				x=open(str(znak)+str(liczba),'wb')
				
				x.write(image.tobytes())
				x.close()
				liczba+=1
				image=Image.new('1',(1000,800))
				imdraw=ImageDraw.Draw(image)
				czy=True
				
		if pygame.mouse.get_pressed()[0]:
			pos = pygame.mouse.get_pos()
			if czy:
				czy=False
				punkt[0]=pos[0]
				punkt[1]=pos[1]
			imdraw.line([(punkt[0],punkt[1]),(pos[0],pos[1])],1,5)
			punkt[0]=pos[0]
			punkt[1]=pos[1]
				
				
		window.fill((0,0,0))
		
		window.blit(pygame.image.frombuffer(image.convert('RGB').tobytes(),(1000,800),'RGB'),(0,0))
		pygame.display.flip()
		clock.tick(60)

		
def nauka(ilosc):
	os.chdir('zdj')
	x=tf.placeholder(tf.float32,[None,4096])
	y=tf.placeholder(tf.float32,[None, 6])
	im=tf.reshape(x,[-1,64,64,1])
	c1=tf.layers.conv2d(im,16,2,1,'same',activation=tf.nn.relu)
	p1=tf.layers.max_pooling2d(c1,2,2)
	c2=tf.layers.conv2d(p1,64,2,1,'same',activation=tf.nn.relu)
	p2=tf.layers.max_pooling2d(c2,2,2)
	flat=tf.layers.flatten(p2)
	l1=tf.layers.dense(flat, 128,tf.nn.relu)
	out=tf.layers.dense(l1,6,tf.nn.sigmoid)
	losss=tf.losses.mean_squared_error(y,out)
	tra=tf.train.AdamOptimizer(0.001).minimize(losss)
	sess=tf.Session()
	saver = tf.train.Saver()
	saver.restore(sess, './grys')
	#sess.run(tf.global_variables_initializer())
	a=[[],[],[],[],[],[],[]]
	test=[]
	os.chdir('..')
	b=os.listdir()
	for i in b:
		if i[0]=='0' or i[0]=='1' or i[0]=='2' or i[0]=='3' or i[0]=='4' or i[0]=='5' or i[0]=='6':
			dd=open(i,'rb')
			lista=list(Image.frombytes('1',(64,64),dd.read()).getdata())
			for j in range(len(lista)):
				if lista[j]==255:
					lista[j]=1
			a[int(i[0])].append(lista)
			dd.close()
	for i in range(6):
		dd=open('T'+str(i),'rb')
		lista=list(Image.frombytes('1',(64,64),dd.read()).getdata())
		for j in range(len(lista)):
			if lista[j]==255:
				lista[j]=1
		test.append(lista)
		dd.close()
	nn=[]
	wyniki=[]
	testy=[]
	for k in range(ilosc):
		n=[]
		llll=random.randint(0,6)
		nn=[[0.0,0.0,0.0,0.0,0.0,0.0]]
		if llll<6:
			nn[0][llll]=1.0
		n=[a[llll][random.randint(0,len(a[llll])-1)]]
		_, lo=sess.run([tra,losss],{x:n,y:nn})
		ou=sess.run([out],{x:test})
		ill=0
		
		for i in range(6):
			mmm=5
			for j in range(5):
				if ou[0][i][j]>ou[0][i][mmm]:
					mmm=j
			if i==mmm:
				ill+=1
		testy.append(ill)
		wyniki.append(lo)
		
	
	plt.cla()
	plt.subplot(2,1,1)
	plt.plot(range(1,len(wyniki)+1),wyniki)
	plt.ylabel('Strata')
	plt.subplot(2,1,2)
	plt.plot(range(1,len(testy)+1),testy)
	plt.ylabel('Testy')
	plt.pause(0.001)
	os.chdir('zdj')
	saver.save(sess, './grys', write_meta_graph=False)

def test():
	os.chdir('zdj')
	x=tf.placeholder(tf.float32,[None,4096])
	y=tf.placeholder(tf.float32,[None, 6])
	im=tf.reshape(x,[-1,64,64,1])
	c1=tf.layers.conv2d(im,16,2,1,'same',activation=tf.nn.relu)
	p1=tf.layers.max_pooling2d(c1,2,2)
	c2=tf.layers.conv2d(p1,64,2,1,'same',activation=tf.nn.relu)
	p2=tf.layers.max_pooling2d(c2,2,2)
	flat=tf.layers.flatten(p2)
	l1=tf.layers.dense(flat, 128,tf.nn.relu)
	out=tf.layers.dense(l1,6,tf.nn.sigmoid)
	sess=tf.Session()
	saver = tf.train.Saver()
	saver.restore(sess, './grys')
	pygame.init()
	window = pygame.display.set_mode((1000, 800))
	pygame.display.set_caption(('Testy'))
	clock = pygame.time.Clock()
	image=Image.new('1',(1000,800))
	imdraw=ImageDraw.Draw(image)
	czy=True
	punkt=[0,0]
	liczba=0
	while True:
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				sys.exit(0)
			if event.type == pygame.MOUSEBUTTONUP:
				lista=list(image.crop(image.getbbox()).resize((64,64)).getdata())
				for j in range(len(lista)):
					if lista[j]==255:
						lista[j]=1
				ou=sess.run(out,{x:[lista]})
				wynik=5
				for i in range(5):
					if ou[0][i]>ou[0][wynik]:
						wynik=i
				if(ou[0][wynik]>0.8):
					print(wynik)
				else:
					print('nic')
				
				image=Image.new('1',(1000,800))
				imdraw=ImageDraw.Draw(image)
				czy=True
				
		if pygame.mouse.get_pressed()[0]:
			pos = pygame.mouse.get_pos()
			if czy:
				czy=False
				punkt[0]=pos[0]
				punkt[1]=pos[1]
			imdraw.line([(punkt[0],punkt[1]),(pos[0],pos[1])],1,5)
			punkt[0]=pos[0]
			punkt[1]=pos[1]
				
				
		window.fill((0,0,0))
		
		window.blit(pygame.image.frombuffer(image.convert('RGB').tobytes(),(1000,800),'RGB'),(0,0))
		pygame.display.flip()
		clock.tick(60)
