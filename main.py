from random import randint
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import cairo
import matplotlib.image as mpli
import neural_network_answer
from PIL import Image
import numpy as np


def get_hieroglyph():
    numbers_list = ['TWO (LIANG)', 'ONE', 'TWO (ER)', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN', 'HUNDRED', 'THOUSAND']
    return numbers_list[randint(0, len(numbers_list) - 1)]


def make_img_array(data):
    xmin = 500
    xmax = 0
    ymin = 500
    ymax = 0
    for stroke in data:
        for point in stroke:
            if point[0] < xmin and point[0] >= 0:
                xmin = int(point[0])
            if point[0] > xmax and point[0] <= 500:
                xmax = int(point[0])
            if point[1] < ymin and point[1] >= 0:
                ymin = int(point[1])
            if point[1] > ymax and point[1] <= 500:
                ymax = int(point[1])
    size = int(max(ymax - ymin, xmax - xmin)) + 10
    array = np.zeros((size, size, 3), np.int8)
    for i in range(size):
        for j in range(size):
            array[i, j, 0] = 255
            array[i, j, 1] = 255
            array[i, j, 2] = 255
    for stroke in data:
        for k in range(len(stroke)):
            have_to_print = [[int(stroke[k][0]), int(stroke[k][1])]]
            if k != 0:
                step = 3
                another_step = 1
                x1 = int(stroke[k - 1][0])
                y1 = int(stroke[k - 1][1])
                x2 = int(stroke[k][0])
                y2 = int(stroke[k][1])
                if x1 == x2:
                    have_to_print = have_to_print + [[x1, i] for i in range(min(y1, y2), max(y1, y2), step)]
                elif y1 == y2:
                    have_to_print = have_to_print + [[i, y1] for i in range(min(x1, x2), max(x1, x2), step)]
                elif abs(x1 - x2) > abs(y1 - y2):
                    factor = abs(y2 - y1) / abs(x2 - x1)
                    if x1 > x2:
                        step = -3
                    if y1 > y2:
                        another_step = -1
                    for x in range(x1, x2, step):
                        have_to_print.append([x, y1 + int(another_step*factor*abs(x - x1))])
                else:
                    factor = abs(x2 - x1) / abs(y2 - y1)
                    if y1 > y2:
                        step = -3
                    if x1 > x2:
                        another_step = -1
                    for y in range(y1, y2, step):
                        have_to_print.append([x1 + int(another_step*factor*abs(y - y1)), y])
            for item in have_to_print:
                for i in range(0, 10):
                    for j in range(0, 10):
                        try:
                            if item[1] + i - ymin >= 0 and item[0] + j - xmin >= 0:
                                array[item[1] + i - ymin, item[0] + j - xmin, 0] = 0
                                array[item[1] + i - ymin, item[0] + j - xmin, 1] = 0
                                array[item[1] + i - ymin, item[0] + j - xmin, 2] = 0
                        except IndexError:
                            continue
    return array


class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, resizable=False)
        self.set_default_size(1000, 700)
        fixed = self.start_container()
        self.add(fixed)
        self.brush = {'width':10, 'color':(1, 1, 1)}
        self.strokes = []
        self.number_hier_accordance = {1 : '一', 2 : '二', 0 : '两', 3 : '三', 4 : '四', 5 : '五', 6 : '六', 7 : '七', 8 : '八', 9 : '九', 10 : '十', 11 : '百', 12 : '千'}


    def start_container(self):
        start_button = Gtk.Button(label="Get random  hieroglyph", name="btn1")
        start_button.set_property("width-request", 200)
        start_button.set_property("height-request", 100)
        fixed = Gtk.Fixed()
        fixed.put(start_button, (1000 - 200) // 2 - 5, (700 - 100) // 2)
        start_button.connect("clicked", self.on_start_button_clicked, fixed)
        return fixed


    def on_start_button_clicked(self, button, container):
        self.remove(container)
        self.new_hieroglyph()


    def on_retry_button_clicked(self, button, container):
        self.remove(container)
        self.new_hieroglyph(hieroglyph = self.answer)


    def new_hieroglyph(self, hieroglyph = None):
        vbox = Gtk.VBox(name = 'random_hier')
        vbox.set_homogeneous(False)
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, True, True, 0)
        if hieroglyph == None:
            self.answer = get_hieroglyph()
        label_left = Gtk.Label(label = 'try to write down the first hieroglyph for: _' + self.answer + '_' + '\n(you may delete everything\nby pressing tre right button of your mouse)')
        label_left.set_justify(Gtk.Justification.CENTER)
        hbox.pack_start(label_left, True, True, 0)
        im_done_button = Gtk.Button(label = "I'm done", name="imd-btn")
        hbox.pack_end(im_done_button, True, True, 0)
        #
        area = Gtk.DrawingArea(name = 'area')
        area.set_property("width-request", 500)
        area.set_property("height-request", 500)
        area.connect("draw", self.draw)
        area.connect('motion-notify-event', self.mouse_move)
        area.connect("button-press-event", self.mouse_press)
        area.connect("button-release-event", self.mouse_release)
        area.set_events(area.get_events() |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK)
        fixed = Gtk.Fixed()
        fixed.put(area, 250, 0)
        fixed.set_property("width-request", 1000)
        fixed.set_property("height-request", 550)
        vbox.pack_end(fixed, False, False, 0)
        im_done_button.connect("clicked", self.stop_writting, vbox, area)
        self.add(vbox)
        self.show_all()
    

    def draw(self, widget, cr):
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.paint()
        for stroke in self.strokes:
            cr.set_source_rgb(self.brush['color'][0], self.brush['color'][1], self.brush['color'][2])
            cr.set_line_width(self.brush['width'])
            cr.set_line_cap(1)
            cr.set_line_join(cairo.LINE_JOIN_ROUND)
            cr.new_path()
            for x, y in stroke:
                cr.line_to(x, y) 
            cr.stroke()


    def mouse_press(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self.strokes.append(list())
            self.strokes[-1].append((event.x, event.y))
            widget.queue_draw()
        elif event.button == Gdk.BUTTON_SECONDARY:
            self.strokes.clear()


    def mouse_move(self, widget, event):
        if event.state:
            self.strokes[-1].append((event.x, event.y))
            widget.queue_draw()


    def mouse_release(self, widget, event):
        widget.queue_draw()


    def stop_writting(self, button, container, area): 
        numbers_list = ['TWO (LIANG)', 'ONE', 'TWO (ER)', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN', 'HUNDRED', 'THOUSAND']
        img = Image.fromarray(make_img_array(self.strokes), 'RGB')
        img = img.resize((28, 28), Image.ANTIALIAS) 
        img.save('img.png')
        self.remove(container)
        self.strokes.clear()
        if neural_network_answer.check(img, numbers_list.index(self.answer)):
            self.allright()
        else:
            self.wrong()

    
    def allright(self):
        numbers_list = ['TWO (LIANG)', 'ONE', 'TWO (ER)', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN', 'HUNDRED', 'THOUSAND']
        label = Gtk.Label(label = 'You are right!\nCongrats!', name = 'labelf')
        label.set_justify(Gtk.Justification.CENTER)
        fixed = self.start_container()
        fixed.put(label, 277, 50)
        label_ans = Gtk.Label(label = 'right answer: ' + self.number_hier_accordance[numbers_list.index(self.answer)], name = 'labelf')
        fixed.put(label_ans, 260, 500)
        self.add(fixed)
        self.show_all()

    def wrong(self):
        numbers_list = ['TWO (LIANG)', 'ONE', 'TWO (ER)', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN', 'HUNDRED', 'THOUSAND']
        label = Gtk.Label(label = "You've made a mistake!\nKeep trying!", name = 'labelf')
        label.set_justify(Gtk.Justification.CENTER)
        fixed = self.start_container()
        fixed.put(label, 130, 50)
        retry_button = Gtk.Button(label="Get the same heirohlyph", name="btn1")
        retry_button.set_property("width-request", 200)
        retry_button.set_property("height-request", 100)
        fixed.put(retry_button, (1000 - 200) // 2 - 5, (700 - 100) // 2 + 150)
        retry_button.connect("clicked", self.on_retry_button_clicked, fixed)
        label_ans = Gtk.Label(label = 'right answer: ' + self.number_hier_accordance[numbers_list.index(self.answer)], name = 'labelf')
        fixed.put(label_ans, 260, 600)
        self.add(fixed)
        self.show_all()


def main():
    cssProvider = Gtk.CssProvider()
    cssProvider.load_from_path('style.css')
    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":    
    main()