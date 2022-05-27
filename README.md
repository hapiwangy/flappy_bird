# flappy_bird
make the game flappy bird and make ai to learn how to play with it
## AI玩的過程
- 每個神經都會操空一隻鳥在玩，所以會有一堆的鳥鳥
- 使用的是neat model
## 判斷是否有單位碰撞
- 使用mask方法:此可以判斷出一個圖中他的每個像素在哪裏，並透過像素(而非邊際)判斷是否有重疊
## 注意
- 後載入的圖片會把先載入的圖片覆蓋掉!!
## 製作遊戲過程
首先要先把此遊戲中的objects都定義出來
以本遊戲為例:background、bird、pipe
- 對於每個物件，定義move方法，用來定義每次刷新畫面的時候需要做的動作