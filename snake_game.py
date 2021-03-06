/*
 * Fuming Qiu
 * Snake game on 16*32 RGB LED matrix
*/

//general setup code
#include <Adafruit_GFX.h>   // Core graphics library
#include <RGBmatrixPanel.h> // Hardware-specific library
#define CLK 8
#define LAT A3
#define OE  9
#define A   A0
#define B   A1
#define C   A2
RGBmatrixPanel matrix(A, B, C, CLK, LAT, OE, false);

//defining buttons
int left = 13;
int right = 12;
int up = 11;
int down = 10;

//timing variables
int eventTime1 = 0;
int eventTime2 = 0;
int eventInc = 0;
unsigned long startTime = 0;
bool next = true;

//snake data
int snakeLen = 10;   ////////////snake len//////////////////////////////////////
int colPxls[100];   //arduino can't append, set 100 as limit
int rowPxls[100];   //ditto
const unsigned long moveRate = 100;   //////////speed//////////////////////
int dRow = 0;
int dCol = 0;
bool newFood = true;
int food[2] = {0, 0};     //these two are both row, col even though
int curHead[2] = {0, 0};  //the matrix does things as col, row





int counter = 0;


void setup() {
  //setup matrix object and pinmodes and random
  matrix.begin();
  pinMode(left, INPUT);
  pinMode(right, INPUT);
  pinMode(up, INPUT);
  pinMode(down, INPUT);
  randomSeed(analogRead(0));

  //display "Snake"
  matrix.setCursor(1, 4);  //col,row
  matrix.setTextColor(matrix.Color333(1,2,1));
  matrix.print("Snake");
  delay(1000);

  //set events and time: 400 ms flash period
  eventTime1 = 0;
  eventTime2 = 400;
  eventInc = 800;
  startTime = millis();

  //flash press to start until right button pressed
  while(digitalRead(right) == LOW) {  
    //start with black screen
    if (millis() - startTime > eventTime1 && next) {
      clearDisp();
      eventTime1 += eventInc;
      next = false;
    }

    //print text
    if (millis() - startTime > eventTime2 && !next) {
      matrix.setCursor(0,0);
      matrix.setTextColor(matrix.Color333(2, 2, 2));
      matrix.print("Push Start");
      next = true;
      eventTime2 += eventInc;
    }
  }

  //clear and draw the border rectangle
  clearDisp();
  matrix.drawRect(0,0, 32, 16, matrix.Color333(7,0,0));

  //start snake at snakeLen long in middle with dCol = 1;
  for (int i = 0; i < snakeLen; i++) {
    rowPxls[i] = 8;
    colPxls[i] = 10 + i;
    matrix.drawPixel(colPxls[i], rowPxls[i], matrix.Color333(2,1,1));
  }
  dCol = 1;
  
  //setup timing
  startTime = millis();
  delay(500);
}

void loop() {  
  //if need new food, find random place for food and turn on that pixel
  if (newFood) {
    newFood = false;
    food[0] = random(1, 14);
    food[1] = random(1, 30);
    matrix.drawPixel(food[1], food[0], matrix.Color333(0, 7, 0));
  }
  
  //if button pressed, update snake motion
  if (digitalRead(up)) {dRow = -1; dCol = 0;}
  else if (digitalRead(down)) {dRow = 1; dCol = 0;}
  else if (digitalRead(left)) {dCol = -1; dRow = 0;}
  else if (digitalRead(right)) {dCol = 1; dRow = 0;}

  //if time to move
  if ((millis() - startTime) > moveRate) {
    //get next head location
    curHead[0] = rowPxls[snakeLen - 1] + dRow;
    curHead[1] = colPxls[snakeLen - 1] + dCol;

    //crash checking: edge = game over
    if (curHead[0] == 0 || curHead[0] == 15 || 
        curHead[1] == 0 || curHead[1] == 31) {
          gameOver();
    }

    //hit self (but tail moved already) = game over
    for (int i = 0; i < snakeLen; i++) {
      if (curHead[0] == rowPxls[i] && curHead[1] == colPxls[i]) {
        gameOver();
      }
    }

    //if ate food, add head, turn it on, increase length, set new food to true
    if (curHead[0] == food[0] && curHead[1] == food[1]) {
      rowPxls[snakeLen] = curHead[0];
      colPxls[snakeLen] = curHead[1];
      matrix.drawPixel(curHead[1], curHead[0], matrix.Color333(2,1,1));
      snakeLen++;
      newFood = true;
    }

    else {
      //turn on the head
      matrix.drawPixel(curHead[1], curHead[0], matrix.Color333(2,1,1));

      //turn off the tail: index 0 in both lists
      matrix.drawPixel(colPxls[0], rowPxls[0], matrix.Color333(0,0,0));

      //remove the tail
      for (int i = 0; i < snakeLen - 1; i++) {
        rowPxls[i] = rowPxls[i + 1];
        colPxls[i] = colPxls[i + 1];
      }

      //add head
      rowPxls[snakeLen - 1] = curHead[0];
      colPxls[snakeLen - 1] = curHead[1];
    }
    
    //update timing
    startTime = millis();
  }
}

void clearDisp() {
  //clears the screen
  matrix.fillScreen(matrix.Color333(0,0,0));
}

void gameOver() {
  //slowly erases board
  for (int i = 0; i < 32; i++) {
    matrix.drawFastVLine(i, 0, 16, matrix.Color333(0,0,0));
    delay(300 - 5 * i);
  }

  //game over screen
  matrix.setCursor(2,0);
  matrix.setTextColor(matrix.Color333(5, 2, 5));
  matrix.print("Game");
  matrix.setCursor(2,9);
  matrix.print("Over");

  //enters infinite loop to force reset
  while(1) {}
}