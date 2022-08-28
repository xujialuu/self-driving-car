#include<WiFi.h>
#include<WebServer.h>

const char *ssid = "ESP32"; //你的网络名称
const char *password = "xujialu1128"; //你的网络密码

WebServer server(80);

const int d1 = 26;
const int d2 = 27;
const int d3 =15;
const int freq = 3000;
const int freq_duo = 50;
const int resolution = 8;
const int channel1 = 0;
const int channel2 = 1;
const int channel3 = 2;
int speed_car = 255;
float angle1 = 6.4;
float angle2 = 32;

void run();
void back();
void stop();
void left();
void right();
void bottom();


void init(){
const char HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
 <head>
    <meta charset='utf-8'>
    <title>小车控制面板</title>
  </head>
  <body>
<h1 id='wenzi'>速度</h1><input id="speed_change" type="range" min='0' max='255' value='255' step='1' style='width:40%;margin-left:30%;'>
    <span id="speed" style='margin-left:5%;'></span>
<h1 id='wenzi'>旋转角度</h1><input id="angle_change" type="range" min='0' max='45' value='45' step='1' style='width:40%;margin-left:30%;'>
    <span id="angle" style='margin-left:5%;'></span>
    <p style='text-align:center'>
    <button type='button' onmousedown='queren()'>确认设置</button> </p> 
    <nav style='text-align:center'>     
    <button type='button' onmousedown='qianjin()'>前进</button>
    <button type='button' onmousedown='houtui()'>后退</button>
    <button type='button' onmousedown='zuozhuan()'>左转</button>
    <button type='button' onmousedown='youzhuan()'>右转</button></nav>
    <p align='center'>
    <button type='button' onmousedown='stop_car()'>停止</button></p>


    <style>
    #wenzi{
      text-align:center;
      font-weight: 1000;
      font-family:'楷体';
      color:blue;
      margin-bottom:5vh}

    </style>



    <script type='text/javascript'>
      var xhttp = new XMLHttpRequest();
      document.getElementById('speed').innerHTML = 255;
      document.getElementById('angle').innerHTML = 45;
      var speed_control = document.getElementById('speed_change');
      var angle_control = document.getElementById('angle_change');
      var speed_num=255,angle_num=45
      speed_control.oninput = function() {
          document.getElementById('speed').innerHTML = this.value;
          speed_num =this.value
        }
      angle_control.oninput = function() {
          document.getElementById('angle').innerHTML = this.value;
          angle_num =this.value
        }
      function queren(){
        xhttp.open('POST','/speed?speed='+speed_num.toString(),true);
        xhttp.send();
        xhttp.open('POST','/angle?angle='+angle_num.toString(),true);
        xhttp.send();
        console.log(speed_num)
        console.log(angle_num)
        }

      function qianjin(){
        xhttp.open('POST','/act?act=qianjin',true);
        xhttp.send();
      }
      function houtui(){
        xhttp.open('POST','/act?act=houtui',true);
        xhttp.send();
      }
      function zuozhuan(){
        xhttp.open('POST','/act?act=zuozhuan',true);
        xhttp.send();
      }
      function youzhuan(){
        xhttp.open('POST','/act?act=youzhuan',true);
        xhttp.send();
      }
      
      function stop_car(){
        xhttp.open('POST','/act?act=stop',true);
        xhttp.send();
      }
    </script>
  </body>
</html>)rawliteral";
  server.send(200,"text/html",HTML);
  }
  void speed_set(){
    String speed_change = server.arg("speed");
    if (speed_change!=NULL){
      speed_car = speed_change.toInt();
      }
  }

  void angle_set(){
     String angle_change = server.arg("angle");
    if (angle_change!=NULL){
      angle1 = 19.2-angle_change.toInt()*12.8/45;
      angle2 = 19.2+angle_change.toInt()*12.8/45;
      
      }
  }

  void move(){   
    String action = server.arg("act");
    if (action=="qianjin"){
      stop();
      bottom();
      run();}
      else if (action=="houtui"){
      stop();
      bottom();
      back();}
      else if (action=="zuozhuan"){
      stop();
      left();
      run();}
      else if (action=="youzhuan"){
      stop();
      right();
      run();}
      else if (action=="stop"){
      stop();}
    }

void setup()
{
  ledcSetup(channel1,freq,resolution);
  ledcAttachPin(d1,channel1);

  ledcSetup(channel2,freq,resolution);
  ledcAttachPin(d2,channel2);

  ledcSetup(channel3,freq_duo,resolution);
  ledcAttachPin(d3,channel3);
  bottom();

  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.softAP(ssid,password);

  Serial.println("IP address: ");
  Serial.println(WiFi.softAPIP()); //打印模块IP  
  
  server.on("/",init);
  server.on("/speed",speed_set);
  server.on("/angle",angle_set);
  server.on("/act",move);
  server.begin();
}

void loop()
{
  server.handleClient();
}

void run(){
  pinMode(d2,OUTPUT);
  digitalWrite(d2,LOW);
  ledcWrite(channel1,speed_car);
}
void back(){
  pinMode(d1,OUTPUT);
  digitalWrite(d1,LOW);
  ledcWrite(channel2,speed_car);
}

void stop(){
  ledcWrite(channel1,0);
  ledcWrite(channel2,0);
}

void left(){
  ledcWrite(channel3,angle1);
  delay(1000);
  }


void right(){
  ledcWrite(channel3,angle2);
  delay(1000);
  }

void bottom(){
  ledcWrite(channel3,19.2);
  delay(1000);
  }
