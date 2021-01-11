from random import random, randint, choice
from copy import deepcopy
from math import log

"""
Обертка для функций, которые будут находиться в узлах,
представляющих функции. Его члены – имя функции, сама функция
и количество принимаемых параметров.
"""
class fwrapper:
    def __init__(self, function, childcount, name):
        self.function = function
        self.childcount = childcount
        self.name = name

"""
Класс функциональных узлов (имеющих потомков). Инициализируется экземпляром класса fwrapper.
Метод evaluate вычисляет значения дочерних узлов и передает их представленной данным узлом
функции в качестве параметров.
"""
class node:
    def __init__(self, fw, children):
        self.function = fw.function
        self.name = fw.name
        self.children = children

    def evaluate(self, inp):
        results = [n.evaluate(inp) for n in self.children]
        return self.function(results)
    
    # Метод display выводит представление дерева в виде строки
    def display(self, indent=0):
        print((' ' * indent) + self.name)
        for c in self.children:
            c.display(indent + 1)

"""
Класс узлов, которые просто возвращают один из переданных программе параметров.
Его метод evaluate возвращает параметр, соответствующий значению idx.
"""
class paramnode:
    def __init__(self, idx):
        self.idx = idx

    def evaluate(self, inp):
        return inp[self.idx]
    
    # Это метод просто печатает индекс возвращаемого параметра
    def display(self, indent=0):
        print('%sp%d' % (' ' * indent, self.idx))

"""
Узлы, возвращающие константы. Метод evaluate просто возвращает
то значение, которым экземпляр был инициализирован.
"""
class constnode:
    def __init__(self, v):
        self.v = v

    def evaluate(self, inp):
        return self.v

    def display(self, indent=0):
        print('%s%d' % (' ' * indent, self.v))

        
"""
Простые функции типа add и subtract можно встроить с помощью лямбда-выражений.
Для остальных функцию придется написать в отдельном блоке.
В любом случае функция обертывается в экземпляр класса fwrapper 
вместе со своим именем и числом параметров.
"""

addw = fwrapper(lambda l: l[0] + l[1], 2, 'add')
subw = fwrapper(lambda l: l[0] - l[1], 2, 'subtract')
mulw = fwrapper(lambda l: l[0] * l[1], 2, 'multiply')


def iffunc(l):
    if l[0] > 0:
        return l[1]
    else:
        return l[2]


ifw = fwrapper(iffunc, 3, 'if')


def isgreater(l):
    if l[0] > l[1]:
        return 1
    else:
        return 0


gtw = fwrapper(isgreater, 2, 'isgreater')

# В этой строке создается список всех функций, чтобы впоследствии из него
# можно было выбирать элементы случайным образом.
flist = [addw, mulw, ifw, gtw, subw]

# C помощью класса node можно построить дерево программы (в качестве примера)
def exampletree():
    return node(ifw, [
        node(gtw, [paramnode(0), constnode(3)]),
        node(addw, [paramnode(1), constnode(5)]),
        node(subw, [paramnode(1), constnode(2)]),
    ]
                )


"""
Эта функция создает узел, содержащий случайно выбранную функцию, и проверяет,
сколько у этой функции должно быть параметров. Для каждого дочернего узла функция
вызывает себя рекурсивно, чтобы создать новый узел. Так конструируется все дерево,
причем процесс построения ветвей завершается в тот момент, когда у очередного узла 
нет дочерних (то есть он представляет либо константу, либо переменную-параметр).
Параметр pc равен числу параметров, принимаемых деревом на входе. Параметр fpr
задает вероятность того, что вновь создаваемый узел будет соответствовать функции,
а ppr – вероятность того, что узел, не являющийся функцией, будет иметь тип paramnode.
"""
def makerandomtree(pc, maxdepth=4, fpr=0.5, ppr=0.6):
    if random() < fpr and maxdepth > 0:
        f = choice(flist)
        children = [makerandomtree(pc, maxdepth - 1, fpr, ppr)
                    for i in range(f.childcount)]
        return node(f, children)
    elif random() < ppr:
        return paramnode(randint(0, pc - 1))
    else:
        return constnode(randint(0, 10))


def hiddenfunction(x, y):
    return x ** 2 + 2 * y + 3 * x + 5


def buildhiddenset():
    rows = []
    for i in range(200):
        x = randint(0, 40)
        y = randint(0, 40)
        rows.append([x, y, hiddenfunction(x, y)])
    return rows


"""
Эта функция перебирает все строки набора данных, вычисляет функцию от указанных 
в ней аргументов и сравнивает с результатом. Абсолютные значения разностей суммируются.
Чем меньше сумма, тем лучше программа, а значение 0 говорит о том, что все результаты 
в точности совпали. 
"""
def scorefunction(tree, s):
    dif = 0
    for data in s:
        v = tree.evaluate([data[0], data[1]])
        dif += abs(v - data[2])
    return dif


"""
Эта функция начинает с корня дерева и решает, следует ли изменить
узел. Если нет, она рекурсивно вызывает mutate для дочерних узлов.
Может случиться, что мутации подвергнутся все узлы, а иногда дерево
вообще не изменится.
"""
# Мутация путем замены поддерева
def mutate(t, pc, probchange=0.1):
    if random() < probchange:
        return makerandomtree(pc)
    else:
        result = deepcopy(t)
        if hasattr(t, "children"):
            result.children = [mutate(c, pc, probchange) for c in t.children]
        return result

"""
Функции, выполняющей скрещивание, передаются два дерева, и она
обходит оба. Если случайно выбранное число не превышает пороговой
вероятности, то функция возвращает копию первого дерева, в которой
одна из ветвей заменена какой-то ветвью, взятой из второго дерева.
Поскольку обход выполняется параллельно, то скрещивание произойдет примерно на одном уровне каждого дерева.
"""
# Функция скрещивания. Две успешные программы комбинируются с целью получения новой программы.
def crossover(t1, t2, probswap=0.7, top=1):
    if random() < probswap and not top:
        return deepcopy(t2)
    else:
        result = deepcopy(t1)
        if hasattr(t1, 'children') and hasattr(t2, 'children'):
            result.children = [crossover(c, choice(t2.children), probswap, 0)
                               for c in t1.children]
        return result

# Функция возвращает функцию ранжирования для имеющегося набора данных
def getrankfunction(dataset):
    def rankfunction(population):
        scores = [(scorefunction(t, dataset), t) for t in population]
        scores.sort()
        return scores

    return rankfunction


"""
Создание конкурентной среды, в которой программы будут эволюционировать.
Смысл в том, чтобы создать набор случайных программ, отобрать из них
наилучшие для копирования и модификации и повторять процесс, пока не будет
выполнено некое условие останова.
"""
def evolve(pc, popsize, rankfunction, maxgen=500, mutationrate=0.1, breedingrate=0.4, pexp=0.7, pnew=0.05):
    """Эта функция создает случайную исходную популяцию, а затем выполняет не более maxgen итераций цикла,
       вызывая каждый раз функцию rankfunction для ранжирования программ от наилучшей до наихудшей.
       Наилучшая программа автоматически попадает в следующее поколение без изменения. 
       Args:
         rankfunction: Функция, применяемая для ранжирования списка программ от наилучшей к наихудшей.
         mutationrate: Вероятность мутации, передаваемая функции mutate.
         breedingrate: Вероятность скрещивания, передаваемая функции crossover.
         popsize: Размер исходной популяции.
         probexp: Скорость убывания вероятности выбора программ с низким рангом. Чем выше значение, тем более суров процесс естественного отбора/
         probnew: Вероятность включения в новую популяцию совершенно новой случайно сгенерированной программы.

       Returns:
        tuple: Найденное наилучшее совпадние

    """
    # Возвращает случайное число, отдавая предпочтение более маленьким числам.
    # Чем меньше значение pexp, тем больше будет доля маленьких чисел.
    def selectindex():
        return int(log(random()) / log(pexp))

    # Создаем случайную исходную популяцию
    population = [makerandomtree(pc) for i in range(popsize)]
    for i in range(maxgen):
        scores = rankfunction(population)
        print(scores[0][0])
        if scores[0][0] == 0: break

        # Две наилучшие особи отбираются всегда
        newpop = [scores[0][1], scores[1][1]]

        # Строим следующее поколение
        while len(newpop) < popsize:
            if random() > pnew:
                newpop.append(mutate(
                    crossover(scores[selectindex()][1],
                              scores[selectindex()][1],
                              probswap=breedingrate),
                    pc, probchange=mutationrate))
            else:
                # Добавляем случайный узел для внесения неопределенности
                newpop.append(makerandomtree(pc))

        population = newpop
    scores[0][1].display()
    return scores[0][1]

#[
#    (10, "program1"),
#    (17, "program2"),
#]

def gridgame(p):
    # Размер доски
    max = (3, 3)

    # Запоминаем последний ход каждого игрока
    lastmove = [-1, -1]

    # Запоминаем положения игроков
    location = [[randint(0, max[0]), randint(0, max[1])]]

    # Располагаем второго игрока на достаточном удалении от первого
    location.append([(location[0][0] + 2) % 4, (location[0][1] + 2) % 4])
    # Не более 50 ходов до объявления ничьей
    for o in range(50):

        # Для каждого игрока
        for i in range(2):
            locs = location[i][:] + location[1 - i][:]
            locs.append(lastmove[i])
            move = p[i].evaluate(locs) % 4

            # Если игрок два раза подряд ходит в одном направлении, ему
            # засчитывается проигрыш
            if lastmove[i] == move: return 1 - i
            lastmove[i] = move
            if move == 0:
                location[i][0] -= 1
                # Доска ограничена
                if location[i][0] < 0: location[i][0] = 0
            if move == 1:
                location[i][0] += 1
                if location[i][0] > max[0]: location[i][0] = max[0]
            if move == 2:
                location[i][1] -= 1
                if location[i][1] < 0: location[i][1] = 0
            if move == 3:
                location[i][1] += 1
                if location[i][1] > max[1]: location[i][1] = max[1]

            # Если противник захвачен в плен, вы выиграли
            if location[i] == location[1 - i]: return i
    return -1


def tournament(pl):
    # Массив для подсчета проигрышей
    losses = [0 for p in pl]

    # Каждый игрок встречается со всеми другими
    for i in range(len(pl)):
        for j in range(len(pl)):
            if i == j: continue

            # Кто выиграл?
            winner = gridgame([pl[i], pl[j]])

            # Два очка за поражение, одно за ничью
            if winner == 0:
                losses[j] += 2
            elif winner == 1:
                losses[i] += 2
            elif winner == -1:
                losses[i] += 1
                losses[i] += 1
                pass

    # Отсортировать и вернуть результаты
    z = list(zip(losses, pl))
    z.sort(key=lambda t: t[0])
    # input()
    print(z[0][1].display(indent=4))
    return z

class humanplayer:
    def evaluate(self, board):

        # Получить мою позицию и позиции других игроков
        me = tuple(board[0:2])
        others = [tuple(board[x:x + 2]) for x in range(2, len(board) - 1, 2)]

        # Нарисовать доску
        for i in range(4):
            for j in range(4):
                if (i, j) == me:
                    print('O',end='  ')
                elif (i, j) in others:
                    print('X',end='  ')
                else:
                    print('.',end='  ')
            print()

        # Показать ходы, для справки
        print('Your last move was %d' % board[len(board) - 1])
        print(' 0')
        print('2 3')
        print(' 1')
        print('Enter move: ')

        # Вернуть введенное пользователем число
        move = int(input())
        return move


class fwrapper:
    def __init__(self, function, params, name):
        self.function = function
        self.childcount = params
        self.name = name


# flist={'str':[substringw,concatw],'int':[indexw]}
flist = [addw, mulw, ifw, gtw, subw]
