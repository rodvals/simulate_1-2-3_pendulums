import matplotlib.pyplot as plt
import numpy as np
#import matplotlib.animation as animation
import copy
from matplotlib.animation import FuncAnimation

#dati iniziali

punti = 600
tempo_simulazione = 10

h = 0.01
g = 9.81
t = 0
framepersec = 20
fps_salta = int((1/h)/framepersec) # ogni quanto devo saltare di scrivere i frame per ottenere framepersec  foto in un secondo
l1, l2, l3 = (1, 1, 1)
m1, m2, m3 = (1, 1, 1)

# condizioni iniziali
# angolo iniziale in gradi
grad0_1, grad0_2, grad0_3 =  (90.01, 0, 0)
theta0_1, theta0_2, theta0_3 =  (grad0_1*2*np.pi / 360 ,grad0_2*2*np.pi / 360 ,grad0_3*2*np.pi / 360)
w0_1, w0_2, w0_3 = ( 0, 0, 0 )
# variabile per contenere q_0 e p_0
def stormer_verlet(f, u):
    u0 = u[0]
    um1 = u[1]
    if(t == 0):
        u0[0:3] += um1[3:6]*h + f(um1, 0)[3:6]*h*h/2
        u0[3:6] = (u0[0:3] - um1[0:3])/h
    # derivazione per ottenere y_1 errore O(h)
    u1 = np.zeros(6)
    u1[0:3] = 2*u0[0:3] - um1[0:3]  + f(u0, t)[3:6]*h*h 
    u1[3:6] = (u1[0:3] - u0[0:3])/h
    u[1] = u0
    u[0] = u1
    return u

def velocity_verlet(f, u):
    s = 1e-14 # valore di soglia per risolvere iterativamente equazione autoconsistente
    diff = [2*s, 2*s, 2*s]
    p = 0
    u0 = u[0]
    y_1 = np.zeros(6)
    # "y_0" prima stima
    y_1[0:3] = u0[0:3] + u0[3:6]*h  + f(u0, t)[3:6]*h*h/2 
    # "y_0" prima stima
    y_1[3:6] = u0[3:6] + f(u0, t)[3:6]*h/2
    add = [0, 0 , 0, 0, 0, 0]
    while (np.abs(diff[0]) > s or np.abs(diff[1]) > s or np.abs(diff[2]) > s):
        diff = add[3:6]
        add =  f(y_1 + add, t)*h/2
        diff -= add[3:6]
        p += 1
    y_1[3:6]+=add[3:6]
    u[0] = y_1
    return 

def runge_kutta4(f, u):
    u0 = u[0]
    k1 = f(u0, t)*h
    k2 = f(u0 + k1/2, t +h/2)*h
    k3 = f(u0 + k2/2 , t + h/2)*h
    k4 = f(u0 + k3 , t + h)*h
    u0 = (u0 + (k1 + 2*k2 + 2*k3 + k4)/6.0)
    u[0] = u0
    #prpply destructive methods on the object int(u0)
    return u


def eulero_esplicito(f, u):
    u0 = u[0]
    u0 = (u0 + f(u0 , t)*h)
    u[0] = u0
    return u


def f_triple(u, t):
	theta_1, theta_2, theta_3 = u[0], u[1], u[2]
	w1, w2, w3 = u[3], u[4], u[5]

	theta_21 = theta_2 - theta_1
	theta_31 = theta_3 - theta_1
	theta_32 = theta_3 - theta_2

	cos_21, cos_31, cos_32 = (np.cos(theta_21), np.cos(theta_31), np.cos(theta_32))
	sin_21, sin_31, sin_32 = (np.sin(theta_21), np.sin(theta_31), np.sin(theta_32))
	sin_1, sin_2, sin_3 = (np.sin(theta_1), np.sin(theta_2), np.sin(theta_3))
	cos_1, cos_2, cos_3 = (np.cos(theta_1), np.cos(theta_2), np.cos(theta_3))

	dw1 = (m3*(g*sin_3 + l1*w1**2*(cos_1*sin_3 - cos_3*sin_1) + l2*w2**2*(cos_2*sin_3 - cos_3*sin_2))*(cos_21*cos_32*m2 + cos_21*cos_32*m3 - cos_31*m2 - cos_31*m3) - (cos_21*m2 + cos_21*m3 - cos_31*cos_32*m3)*(g*m2*sin_2 + g*m3*sin_2 + l1*m2*w1**2*(cos_1*sin_2 - cos_2*sin_1) + l1*m3*w1**2*(cos_1*sin_2 - cos_2*sin_1) - l3*m3*w3**2*(cos_2*sin_3 - cos_3*sin_2)) + (-cos_32**2*m3 + m2 + m3)*(g*m1*sin_1 + g*m2*sin_1 + g*m3*sin_1 - l2*m2*w2**2*(cos_1*sin_2 - cos_2*sin_1) - l2*m3*w2**2*(cos_1*sin_2 - cos_2*sin_1) - l3*m3*w3**2*(cos_1*sin_3 - cos_3*sin_1)))/(l1*(cos_21**2*m2**2 + 2*cos_21**2*m2*m3 + cos_21**2*m3**2 - 2*cos_21*cos_31*cos_32*m2*m3 - 2*cos_21*cos_31*cos_32*m3**2 + cos_31**2*m2*m3 + cos_31**2*m3**2 + cos_32**2*m1*m3 + cos_32**2*m2*m3 + cos_32**2*m3**2 - m1*m2 - m1*m3 - m2**2 - 2*m2*m3 - m3**2))

	dw2 = (-m3*(g*sin_3 + l1*w1**2*(cos_1*sin_3 - cos_3*sin_1) + l2*w2**2*(cos_2*sin_3 - cos_3*sin_2))*(-cos_21*cos_31*m2 - cos_21*cos_31*m3 + cos_32*m1 + cos_32*m2 + cos_32*m3) - (cos_21*m2 + cos_21*m3 - cos_31*cos_32*m3)*(g*m1*sin_1 + g*m2*sin_1 + g*m3*sin_1 - l2*m2*w2**2*(cos_1*sin_2 - cos_2*sin_1) - l2*m3*w2**2*(cos_1*sin_2 - cos_2*sin_1) - l3*m3*w3**2*(cos_1*sin_3 - cos_3*sin_1)) + (-cos_31**2*m3 + m1 + m2 + m3)*(g*m2*sin_2 + g*m3*sin_2 + l1*m2*w1**2*(cos_1*sin_2 - cos_2*sin_1) + l1*m3*w1**2*(cos_1*sin_2 - cos_2*sin_1) - l3*m3*w3**2*(cos_2*sin_3 - cos_3*sin_2)))/(l2*(cos_21**2*m2**2 + 2*cos_21**2*m2*m3 + cos_21**2*m3**2 - 2*cos_21*cos_31*cos_32*m2*m3 - 2*cos_21*cos_31*cos_32*m3**2 + cos_31**2*m2*m3 + cos_31**2*m3**2 + cos_32**2*m1*m3 + cos_32**2*m2*m3 + cos_32**2*m3**2 - m1*m2 - m1*m3 - m2**2 - 2*m2*m3 - m3**2))

	dw3 = ((g*sin_3 + l1*w1**2*(cos_1*sin_3 - cos_3*sin_1) + l2*w2**2*(cos_2*sin_3 - cos_3*sin_2))*(-cos_21**2*m2**2 - 2*cos_21**2*m2*m3 - cos_21**2*m3**2 + m1*m2 + m1*m3 + m2**2 + 2*m2*m3 + m3**2) + (cos_21*cos_32*m2 + cos_21*cos_32*m3 - cos_31*m2 - cos_31*m3)*(g*m1*sin_1 + g*m2*sin_1 + g*m3*sin_1 - l2*m2*w2**2*(cos_1*sin_2 - cos_2*sin_1) - l2*m3*w2**2*(cos_1*sin_2 - cos_2*sin_1) - l3*m3*w3**2*(cos_1*sin_3 - cos_3*sin_1)) - (-cos_21*cos_31*m2 - cos_21*cos_31*m3 + cos_32*m1 + cos_32*m2 + cos_32*m3)*(g*m2*sin_2 + g*m3*sin_2 + l1*m2*w1**2*(cos_1*sin_2 - cos_2*sin_1) + l1*m3*w1**2*(cos_1*sin_2 - cos_2*sin_1) - l3*m3*w3**2*(cos_2*sin_3 - cos_3*sin_2)))/(l3*(cos_21**2*m2**2 + 2*cos_21**2*m2*m3 + cos_21**2*m3**2 - 2*cos_21*cos_31*cos_32*m2*m3 - 2*cos_21*cos_31*cos_32*m3**2 + cos_31**2*m2*m3 + cos_31**2*m3**2 + cos_32**2*m1*m3 + cos_32**2*m2*m3 + cos_32**2*m3**2 - m1*m2 - m1*m3 - m2**2 - 2*m2*m3 - m3**2))

	return np.array([ w1, w2, w3 , dw1, dw2, dw3])


def f_double( u , t):
	theta_1, theta_2 = u[0], u[1]
	w1, w2 = u[3], u[4]

	theta_12 = theta_1 - theta_2

	cos_12 = np.cos(theta_12)
	sin_12 = np.sin(theta_12)
	sin_1, sin_2 = (np.sin(theta_1), np.sin(theta_2))
	cos_1, cos_2 = (np.cos(theta_1), np.cos(theta_2))

	dw1 = (-sin_12*(m2*l1*w1**2 * cos_12 + m2*l2*w2**2) - g*((m1+m2)*sin_1 - m2*sin_2 * cos_12))/(l1*(m1 + m2* sin_12**2))
	dw2 = (sin_12 * ((m1+m2)*l1*w1**2 + m2*l2*w2**2 * cos_12) + g*((m1+m2)*sin_1 * cos_12 - (m1+m2)*sin_2))/(l2*(m1+m2*sin_12**2))   

	return np.array([ w1, w2, 0, dw1, dw2, 0])


def f_single( u , t):
	theta_1 = u[0]
	w1 = u[1]      
	dw1 = -g/l1 * np.sin(theta_1)
	return np.array([ w1, 0, 0, dw1, 0, 0])



def get_xy_coords(q):
	x1 = l1*np.sin(q[0])
	x2 = l2*np.sin(q[1]) + x1
	x3 = l3 * np.sin(q[2]) + x2
	y1 = -l1*np.cos(q[0]) 
	y2 = -l2*np.cos(q[1]) + y1 
	y3 = -l3 * np.cos(q[2]) + y2
	x = (x1, x2, x3)
	y = (y1, y2, y3)
	return x, y 

def get_polar_coords(p):
	x, y = get_xy_coords(p)
	r1 = np.sqrt(x[0]*x[0] + y[0]*y[0])
	r2 = np.sqrt(x[1]*x[1] + y[1]*y[1])
	r3 = np.sqrt(x[2]*x[2] + y[2]*y[2])
	return (p[0], p[1], p[2]), (r1, r2, r3)


def get_xy_velocity(p):
	dx1 = -l1*np.cos(p[0])*p[3]
	dx2 = -l2*np.cos(p[1])*p[4] + dx1
	dx3 = -l3 * np.cos(p[2])*p[5] + dx2
	dy1 = -l1*np.sin(p[0])*p[3]
	dy2 = -l2*np.sin(p[1])*p[4] + dy1 
	dy3 = -l3 * np.sin(p[2])*p[5] + dy2
	return (dx1, dx2, dx3), (dy1, dy2, dy3)

def energia_cinetica(p):
	dx, dy = get_xy_velocity(p)
	dx1 = -l1*np.cos(p[0])*p[3]
	dx2 = -l2*np.cos(p[1])*p[4] + dx1
	dx3 = -l3 * np.cos(p[2])*p[5] + dx2
	dy1 = -l1*np.sin(p[0])*p[3] 
	dy2 =  -l2*np.sin(p[1])*p[4] + dy1 
	dy3 = -l3 * np.sin(p[2])*p[5] + dy2
	ek = (dx[0]**2 + dx[1]**2 + dx[2]**2 + dy[0]**2 + dy[1]**2 + dy[2]**2)/2.
	return ek

def energia_potenziale(p):
	x, y = get_xy_coords(p)
	ep = g*(m1*y[0]+m2*y[1]+m3*y[2])
	return ep

def energia_totale(p):
	return energia_cinetica(p) + energia_potenziale(p)
    

def animate_triple_pendulum(f, output):
    global t, tempo_simulazione, h
    t = 0
    x1_plot = []
    x2_plot = []
    x3_plot = []
    y1_plot = []
    y2_plot = []
    y3_plot = []
    r1_plot = []
    r2_plot = []
    r3_plot = []
    theta1_plot = []
    theta2_plot = []
    theta3_plot = []

    u0 = np.array([theta0_1, theta0_2, theta0_3, w0_1, w0_2, w0_3])
    um1 = np.array([theta0_1, theta0_2, theta0_3, w0_1, w0_2, w0_3])
    u = np.array([u0, um1])

    fps= punti/tempo_simulazione
    fig = plt.figure()
    ax_pend = plt.subplot(221)
    ax_polar = fig.add_subplot(222, projection='polar')
    ax_polar.set_theta_offset(np.pi/2)
    ax_en_tot = fig.add_subplot(223)
    ax_en_k_p = fig.add_subplot(224)

    ax_pend.set_aspect('equal', adjustable='box')
    ax_pend.axis('off')
    ax_pend.set(xlim=(-(l1+l2+l3)*1.2, (l1+l2+l3)*1.2), ylim=(-(l1+l2+l3)*1.2, (l1+l2+l3)*1.2))

# lines from a mass to another
    line1, = ax_pend.plot([], [], color='k', linestyle='-', linewidth=2)    
    line2, = ax_pend.plot([], [], color='k', linestyle='-', linewidth=2)    
    line3, = ax_pend.plot([], [], color='k', linestyle='-', linewidth=2)    

# tail and points
    line1_tail, = ax_pend.plot([], [], 'o-',color = '#d2eeff',markersize = 12, markerfacecolor = '#0077BE',linewidth=2, markevery=10000, markeredgecolor = 'k')   # line for Earth
    line2_tail, = ax_pend.plot([], [], 'o-',color = '#ff3bd2',markersize = 12, markerfacecolor = '#f66338',linewidth=2, markevery=10000, markeredgecolor = 'k')   # line for Earth
    line3_tail, =  ax_pend.plot([], [], 'o-',color = '#af3bd2',markersize = 12, markerfacecolor = '#af6338',linewidth=2, markevery=10000, markeredgecolor = 'k')   # line for Earth
    time_text = ax_pend.text(0.02, 0.95, '', transform=ax_pend.transAxes)
    energy_text = ax_pend.text(0.02, 0.90, '', transform=ax_pend.transAxes)

# graphs 
    en_tot = [energia_totale(u0)]
    en_k = [energia_cinetica(u0)]
    en_p = [energia_potenziale(u0)]
    scatti_xy = [get_xy_coords(u0)]
    theta, r = get_polar_coords(u0)
    

    fig.set_figheight(8)
    fig.set_figwidth(8)
     
    def init():
        line1.set_data([], [])
        line2.set_data([], [])
        line3.set_data([], [])
        line1_tail.set_data([], [])
        line2_tail.set_data([], [])
        line3_tail.set_data([], [])
        time_text.set_text('')
        energy_text.set_text('')
        return line, time_text, energy_text

    def animate(i):
        global t
        nonlocal u
        tail1 = 10
        tail2 = 10
        tail3 = 10
        for x in range(fps_salta):
            u = f(f_triple, u)
            t+=h
        u0 = u[0]

        x, y = get_xy_coords(u0)

        x1_plot.append(x[0])
        x2_plot.append(x[1])
        x3_plot.append(x[2])
        y1_plot.append(y[0])
        y2_plot.append(y[1])
        y3_plot.append(y[2])

        theta, r = get_polar_coords(u0)
        theta1_plot.append(theta[0])
        theta2_plot.append(theta[1])
        theta3_plot.append(theta[2])

        r1_plot.append(r[0])
        r2_plot.append(r[1])
        r3_plot.append(r[2])

        scatti_xy.append([x, y])
        en_tot.append(energia_totale(u0))
        en_k.append(energia_cinetica(u0))
        en_p.append(energia_potenziale(u0))

        # line from the origin to the first mass
        line1.set_data([0, x[0]], [0, y[0]])
        # line from the first mass to the second mass
        line2.set_data([x[0], x[1]], [y[0], y[1]])
        # line from the second to the third mass
        line3.set_data([x[1], x[2]], [y[1], y[2]])
        line1_tail.set_data(x1_plot[i:max(1,i-tail1):-1], y1_plot[i:max(1,i-tail1):-1])
        line2_tail.set_data(x2_plot[i:max(1,i-tail2):-1], y2_plot[i:max(1,i-tail2):-1])
        line3_tail.set_data(x3_plot[i:max(1,i-tail3):-1], y3_plot[i:max(1,i-tail3):-1])
        time_text.set_text('time = %.1f' % (t))
        energy_text.set_text('energy = %.9f J' % en_tot[i])
        
        ax_en_tot.clear()
        ax_en_k_p.clear()
        ax_polar.clear()
        ax_polar.set_theta_zero_location("S")

        ax_polar.plot(theta1_plot, r1_plot)
        ax_polar.plot(theta2_plot, r2_plot)
        ax_polar.plot(theta3_plot, r3_plot)
        ax_en_tot.plot(en_tot, label='Energia Totale')
        ax_en_k_p.plot(en_k, label='Energia Cinetica')
        ax_en_k_p.plot(en_p, label='Energia Potenziale')
        return line1, line2, line3, line1_tail, line2_tail, line3_tail

    
    duration = tempo_simulazione
    anim = FuncAnimation(fig, func = animate, interval=int(1000/framepersec), frames = framepersec * tempo_simulazione, repeat = False, blit =False)
#    anim.save(output)
    plt.show()
    return anim

animate_triple_pendulum(stormer_verlet, "sv_triple.mp4")
animate_triple_pendulum(runge_kutta4, "rk.mp4")
animate_triple_pendulum(eulero_esplicito, "eulero_exp.mp4")
#anim_pend = animate_single_pendulum(stormer_verlet, "sv_single.mp4")
#anim_pend = animate_double_pendulum(velocity_verlet, "vv_double.mp4")
