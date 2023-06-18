# Механічний кіт у пошуках коробок

**Зміст** 

1. [Інкапсуляція](#інкапсуляція)
2. [Розробка алгоритму](#розробка-алгоритму)
    * [Алгоритм словесно](#алгоритм-словесно)
    * [Алгоритм графічно (приклад виконання)](#алгоритм-графічно-приклад-виконання)
3. [Використані бібліотеки](#використані-бібліотеки)
4. [Підрахунок складності](#підрахунок-складності)
5. [Висновки](#висновки)
    * [Чи буде залежати результат алгоритму від розташування  початкової клітинки?](#чи-буде-залежати-результат-алгоритму-від-розташування-початкової-клітинки)
6. [Інструкція з використання](#інструкція-з-використання)
7. [Контакти автора](#контакти-автора)
8. [Джерела](#джерела)

## Інкапсуляція
---
Маємо справу із двома сутностями, для яких необхідно буде встановлювати та/або змінювати параметри: **Кімната** та **Кіт**.
Тож, маємо два класи - **Room** та **Cat** відповідно.
```
class Room:
    # constructor that holds value for territory_size (matrix dimension), boxes count (boxes to randomize)
    def __init__(self, territory_size, boxes_count):
        self.N = territory_size # dimensions for the initial matrix
        self.territory = np.zeros((territory_size, territory_size)) # filling the initial matrix with zeroes
        self.BOX = boxes_count # quantity of boxes to randomize
        # in case it made duplicate points we ensure there are exactly boxes_count points
        while len(np.where(self.territory==1)[0]) < boxes_count:
            # randomized boxes are shown as "ones"
            self.territory[random.randint(0, territory_size)][random.randint(0, territory_size)] = 1
            
    N = 0 # matrix size
    BOX = 0 # initial box count
    territory = [] # initial matrix

class Cat:
    # constructor that recieves a set Room object
    def __init__(self, terr: Room):
        self.cat_pos_i = random.randint(0, terr.N) # initial x position of cat to start from
        self.cat_pos_j = random.randint(0, terr.N) # initial y position of cat to start from
        self.map_visited = np.full_like(terr.territory, 0) # an N-sized matrix to track the progress
        self.boxes_left_count = terr.BOX # quantity of boxes to randomize
        self.max_dist_to_move = 2*self.VIS+1 # maximum cells for the cat to look at once (in a straight line)

    cat_pos_i = 0 # current cat position (x)
    cat_pos_j = 0 # current cat position (y)
    VIS = 3 # cat vision ability (in cells, around)
    map_visited = [] # cat's map (where it has already been)
    boxes_to_pick = [] # current boxes to pick in a queue
    boxes_left_count = 0 # quantity of boxes yet to be found
    prev_directions = [] # previous directions the cat had followed
    max_dist_to_move = 0 # maximum cells for the cat to look at once (in a straight line)

    # territory - the initial matrix; room
    # returns [submatrix VISxVIS, respective borders to get that submatrix from the room matrix]
    def look_around(self, territory: np.ndarray) # memorizes location around the cat
    # terr_size - the initial matrix size
    def get_direction(self, terr_size: int) # decides the direction to move further
    # territory - the initial matrix; room
    def search_for_boxes(self, territory: np.ndarray) # finds boxes in location using look_around()
    # returns cat's (x,y) position
    def get_cat_pos(self) # gets current cat position
    # coords - coordinates for cat to go to
    def move_to(self, coords: tuple) # moves the cat to the specific coordinates
    # territory - the initial matrix; room
    def take_the_boxes(self, territory: np.ndarray) # takes the boxes found by search_for_boxes(), meanwhile searching for new boxes
    # terr - Room object
    def move_down(self, terr: Room) # moves down exactly max_dist_to_move or less, if necessary
    # territory - the initial matrix; room
    def move_up(self, territory: np.ndarray) # moves up exactly max_dist_to_move or less, if necessary
    # terr - Room object
    def move_right(self, terr: Room) # moves up exactly max_dist_to_move or less, if necessary; can't call itself 
    # territory - the initial matrix; room
    def return_to_start(self, territory: np.ndarray) # return to the upper-left corner of the room
    # terr - Room object
    def location_search(self, terr: Room) # look for remaining boxes
```

## Розробка алгоритму
---
Для кращого розуміння пропоную розглянути словесну та графічну версію (з прикладом).

---
### Алгоритм словесно
Алгоритм повинен найбільш вдало підлаштовуватися під початкову (відправну) точку появи котика, так само як і під генерацію коробок. Немає необхідності перебирати по клітинці (повним перебором), оскільки кіт може бачити доволі широко.

Загальна ідея до реалізації полягає у тому, щоб за найменшу кількість ходів знайти всі коробки із можливістю запобігання **постійного** звертання до **повного перебору**.

Механічний котик буде рухатися "змійкою" із пріоритетним напрямом вниз. Всі коробки, що знаходяться на шляху підбираємо і продовжуємо алгоритм з цієї точки, не повертаючись назад. 

Для кращого розуміння розглянемо зображення та словесним алгоритм із загальною ідеєю:

0. Кіт з'являється у випадковій точці та перевіряє, чи є куди рухатися вниз (його поточні координати + радіус огляду враховуються, тож не до "упору"). Якщо ні - рухаємося вправо. Закінчуємо, якщо коробок більше немає. Далі працюємо лише за списком "якщо" (перевіряючи виключно зверху вниз):
1. Якщо попередній рух був вгору або вниз. 
Якщо є куди, то рухаємося вправо. Інакше - переміщуємося до центру матриці (ділення значення N на 2 без залишку) та по головній діагоналі  переходимо у точку (0,0), перевіряючи шляхом всі коробки. Закінчуємо, якщо коробок більше немає.
2. Якщо попередній рух був вправо і більше змоги рухатися вправо немає і це тільки другий рух, то рухаємося вниз, якщо є куди. Інакше - переміщуємося до центру матриці (ділення значення N на 2 без залишку) та по головній діагоналі переходимо у точку (0,0), перевіряючи шляхом всі коробки. Закінчуємо, якщо коробок більше немає.
3. Якщо попередній рух був вправо і більше змоги рухатися вправо немає і рухів до цього було більше ніж один. Якщо рух перед попереднім був вниз, то рухаємося догори, переміщуємося до центру матриці (ділення значення N на 2 без залишку) та по головній діагоналі переходимо у точку (0,0), перевіряючи шляхом всі коробки. Закінчуємо, якщо коробок більше немає. Інакше - рухаємося вниз і переміщуємося до центру матриці (ділення значення N на 2 без залишку) та по головній діагоналі переходимо у точку (0,0), перевіряючи шляхом всі коробки. Закінчуємо, якщо коробок більше немає.
4. Інакше. Якщо це тільки другий рух, то рухаємося вгору. Інакше, якщо рух перед попереднім був вниз, то рухаємося вгору. Інакше, рухаємося вниз. Закінчуємо, якщо коробок більше немає.
---
### Алгоритм графічно (приклад виконання)
Нехай дано матрицю 30х30. Стартова позиція котика позначена як "С", коробки 6 штук - як "1". Червона рамка свідчить про оглядову здатність котика.

![Algorithm grafically](/assets/image-1.png)

Крок 1. Рухаємося вниз, адже є куди. Максимум на 2*V+1 клітинок, де V=3 та символізує радіус огляду. Спускаємося лише на 6 пунктів, тому що радіус огляду дозволяє охопити всю необхідну область. Знайдено першу коробку. Переходимо до неї. Тепер знайдено другу. Переходимо на неї. Більше коробок поряд немає, переходимо до кроку 2.

Крок 2. Рухаємося вправо (1 раз для будь-якого "право"). Знову не беремо максимальну дистанцію, а підлаштовуємося під кут огляду. Для зручного сприйняття подальшого алгоритму надалі область огляду позначатися не буде.

Крок 3. Йдемо нагору, шукаючи коробки. Жодної не знайдено. Внизу вже були, вправо більше немає куди. 

Крок 4. Повертаємося на (0,0) через центр матриці та головну діагональ (4.1 -> 4.2).

Крок 5. Рухаємося вниз (завжди пріоритетний напрям). Коробок не знайдено.

Крок 6. Вправо (1 раз).

Крок 7. Вгору на макс. відстань. Знаходимо дві коробки, беремо їх послідовно (7.1). Все ще продовжуємо розпочатий рух вгору (7.2), але від останньої коробки.

Крок 8. Вправо.

Крок 9. Вниз; знаходимо останні коробки, беремо їх. Більше коробок немає, алгоритм закінчено.

## Використані бібліотеки
---
**NumPy** - для зручної, ефективної та швидкої роботи зі списками, у тому числі багатовимірними.

Модуль **random** для використання реалізованих функцій для створення "випадкових" чисел.

## Підрахунок складності
---
Приблизний підрахунок складності реалізуємо за допомогою [**Big O notation**](https://www.simplilearn.com/big-o-notation-in-data-structure-article#:~:text=Big%20O%20Notation%20is%20a%20tool%20used%20to%20describe%20the,time%20complexity%20of%20an%20algorithm.), який орієнтується вважати складністю алгоритму максимальну складність, яка може виникнути у найгіршому випадку його виконання.

Враховуючи те, що у програмі присутні цикли, рекурсивні функції і т.п., елементарні операції та їх константну складність **O(c)** не розглядатимемо.

Зосереджуватись на складності **O(n)** циклів, теж не будемо, одразу переходимо до рекурсивних функцій.

Список рекурсивних методів:

**take_the_boxes**: зовнішній цикл максимум N разів - лінійна складність; функція у гіршому випадку викличе себе N разів, коли коробки будуть зустрічатися підряд, і при цьому, зовнішній цикл виконається лише 1 раз - складність **О(n)**.

**move_up** - цикл

```
for i in range(0, undiscovered_cells_up // self.max_dist_to_move)
```
 буде продовжуватись, **"поділ відбувається націло" разів** та залежить від вхідних параметрів N та V, залежність логарифмічна: 

log<sub>2*V+1</sub>(N),

але всередині ще є функція **take_the_boxes**, яка теж може себе викликати. Маємо дві рекурсивні функції всередині рекурсивної функції логарифмічної складності. Загалом, маємо:

$N^{2}$ * log<sub>2*V+1</sub>(N)

**move_down** - за складністю аналог функції move_up.
return_to_start - також не перевищує складності вищезгаданих функцій.

## Висновки
---
Алгоритм працює тим краще, чим коробки розташовані ближче одна до одної та наближені до центру. Також алгоритм виказує найбільшу ефективність, коли розташування наступної коробки пов'язано із розташуванням попередньої лінійно.

### Чи буде залежати складність алгоритму від розташування  початкової клітинки?
---
Так, якщо кіт з'являється далі від коробок, то кроків буде виконано більше, у тому числі рекурсивних.

## Інструкція з використання
---
Файл запускати згідно з вимогами встановленого компілятора. У папці з файлом **index.py**:
```
py index.py
```
або:
```
python index.py
```

## Контакти автора
---
Дзбановський Юрій
* Email: uradzb@ukr.net
* Telegram: +38 096 874 17 18
* Viber: +38 096 874 17 18

## Джерела
---
1. https://adrianmejia.com/how-to-find-time-complexity-of-an-algorithm-code-big-o-notation/
2. https://stackoverflow.com/questions/13467674/determining-complexity-for-recursive-functions-big-o-notation