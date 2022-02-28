#!/usr/bin/python
# -*- coding: utf-8 -*-

# Este NÃO é um programa ROS

from __future__ import print_function, division 

import cv2
import os,sys, os.path
import numpy as np
import math

def encontrar_foco(D,H,h):
    """Não mude ou renomeie esta função
    Entradas:
       D - distancia real da câmera até o objeto (papel)
       H - a distancia real entre os circulos (no papel)
       h - a distancia na imagem entre os circulos
    Saída:
       f - a distância focal da câmera
    """
    f = h*(D/H)

    return f

def segmenta_circulo_ciano(hsv): 
    """Não mude ou renomeie esta função
    Entrada:
        hsv - imagem em hsv
    Saída:
        mask - imagem em grayscale com tudo em preto e os pixels do circulos ciano em branco
    """
    # Segmenta apenas a cor violeta
    menor = (int(160/2) - 10, 70, 70)
    maior = (int(240/2) + 10, 255, 255)
    mask_ciano = cv2.inRange(hsv, menor, maior)
    return mask_ciano
    

def segmenta_circulo_magenta(hsv):
    """Não mude ou renomeie esta função
    Entrada:
        hsv - imagem em hsv
    Saída:
        mask - imagem em grayscale com tudo em preto e os pixels do circulos magenta em branco
    """
    # Segmenta apenas a cor violeta
    menor = (130, 40, 40)
    maior = (175, 255, 255)
    mask_magenta = cv2.inRange(hsv, menor, maior)
    return mask_magenta
def encontrar_maior_contorno(segmentado):
    """Não mude ou renomeie esta função
    Entrada:
        segmentado - imagem em preto e branco
    Saída:
        contorno - maior contorno obtido (APENAS este contorno)
    """
    contornos, arvore = cv2.findContours(segmentado.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    maior = None  
    maior_area = 0
    for c in contornos:
        area = cv2.contourArea(c)
        if area > maior_area:
            maior_area = area
            maior = c 

    return maior

def encontrar_centro_contorno(contorno):
    """Não mude ou renomeie esta função
    Entrada:
        contorno: um contorno (não o array deles)
    Saída:
        (Xcentro, Ycentro) - uma tuple com o centro do contorno (no formato 'int')!!! 
    """  
    
    M = cv2.moments(contorno)

    Xcentro = int(M["m10"] / M["m00"])
    Ycentro = int(M["m01"] / M["m00"])

    return (Xcentro, Ycentro)

def calcular_h(centro_ciano, centro_magenta):
    """Não mude ou renomeie esta função
    Entradas:
        centro_ciano - ponto no formato (X,Y)
        centro_magenta - ponto no formato (X,Y)
    Saída:
        distancia - a distancia Euclidiana entre os pontos de entrada 
    """
    
    distX = centro_ciano[0] - centro_magenta[0]
    distY = centro_ciano[1] - centro_magenta[1]

    distancia = ( (distX)**2 + (distY)**2 )**0.5

    return distancia

def encontrar_distancia(f,H,h):
    """Não mude ou renomeie esta função
    Entrada:
        f - a distância focal da câmera
        H - A distância real entre os pontos no papel
        h - a distância entre os pontos na imagem
    Saída:
        D - a distância do papel até câmera
    """
    try:
        D = f*H/h
    except:
        D =0 
    return D
    

def calcular_distancia_entre_circulos(img):
    """Não mude ou renomeie esta função
    Deve utilizar as funções acima para calcular a distancia entre os circulos a partir da imagem BGR
    Entradas:
        img - uma imagem no formato BGR
    Saídas:
        h - a distância entre os os circulos na imagem
        centro ciano - o centro do círculo ciano no formato (X,Y)
        centro_magenta - o centro do círculo magenta no formato (X,Y)
        img_contornos - a imagem com os contornos desenhados
    """
    try:
        img_contornos = img.copy()
        # Transformando para hsv
        img_hsv = cv2.cvtColor(img_contornos, cv2.COLOR_BGR2HSV)
        # magenta segmentada e ciano segmentado
        magenta_circle = segmenta_circulo_magenta(img_hsv)
        ciano_circle = segmenta_circulo_ciano(img_hsv)
        # encontrando o maior contorno segmentado
        magenta_contorno = encontrar_maior_contorno(magenta_circle)
        ciano_contorno = encontrar_maior_contorno(ciano_circle)
        # centro dos contornos
        centro_magenta = encontrar_centro_contorno(magenta_contorno)
        centro_ciano = encontrar_centro_contorno(ciano_contorno)
        # distância entre centros dos contornos
        h = calcular_h(centro_ciano, centro_magenta)
        # Desenhando os contornos
        cv2.drawContours(img_contornos, ciano_contorno, -1, (0, 0, 255), 3)
        cv2.drawContours(img_contornos, magenta_contorno, -1, (255, 0, 0), 3)
    except:
        h, centro_ciano, centro_magenta, img_contornos = 0,(0,0),(0,0),img

    return h, centro_ciano, centro_magenta, img_contornos

def calcular_angulo_com_horizontal_da_imagem(centro_ciano, centro_magenta):
    """Não mude ou renomeie esta função
        Deve calcular o angulo, em graus, entre o vetor formato com os centros do circulos e a horizontal.
    Entradas:
        centro_ciano - centro do círculo ciano no formato (X,Y)
        centro_magenta - centro do círculo magenta no formato (X,Y)
    Saídas:
        angulo - o ângulo entre os pontos em graus
    """
    
    # achando coordenadas do centro da magenta e do ciano
    xm, ym = centro_magenta[0], centro_magenta[1]
    xc, yc = centro_ciano[0], centro_ciano[1]
    # achando coordenadas do ponto médio
    xcm = (xm+xc)/2
    ycm = (ym+yc)/2
    
    # achando lados do triangulo
    l = ((xm-xc)**2+(ym-ycm)**2)**0.5
    l1 = xcm-xc
    l2 = ((xm-xcm)**2+(ym-ycm)**2)**0.5
    if l1 == 0 or l2 == 0:
        angulo = 0
    else:
        angulo = math.degrees(math.acos((l1**2 + l2**2 - l**2)/(2*l1*l2)))

    return angulo
