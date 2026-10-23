# Maizuru_Akebono3
第11回廃炉創造ロボコン舞鶴高専チーム[まいづる]リポジトリへようこそ

## Team Members
> 名倉 時春　**[Reader]**

> 山城 喬楽　**[CAD]**

> 内橋 慧悟　**[ECD]**

> 北条 博輝　**[CAD]**

> 池田 紗也野 **[SSV]** 

> 宮川 颯季　**[Fitter]**

> 和泉 穂花　**[Fitter]**

> 岩本 千尋　**[Fab]**

> 高岡 優羽　**[PG (Repository Host)]**

> 坂田 雄哉　**[SSS (Super Super Supporter)]**

## Commit Rules
コミットメッセージの初めには必ず prefix をつける様にしましょう.  
[参考：僕が考える最強のコミットメッセージの書き方(Qiita)](https://qiita.com/konatsu_p/items/dfe199ebe3a7d2010b3e)

| Prefix   | 意味                                                    |
| -------- | ------------------------------------------------------- |
| add      | ちょっとしたファイルやコードの追加(画像など)            |
| change   | ちょっとしたファイルやコードの変更(画像差し替え)        |
| feat     | ユーザが利用する機能の追加(add/change を内包しても良い) |
| style    | 機能部分を変更しない、コードの見た目の変化(CSS)         |
| refactor | リファクタリング                                        |
| fix      | バグ修正                                                |
| remove   | ファイルなどの削除                                      |
| test     | テスト関連                                              |
| move     | フォルダの移動                                         |
| chore    | ビルド、補助ツール、ライブラリ関連                      |


# Windows
## 初めて動かす際の初期設定
Windows環境で本リポジトリのプログラムを動作させるためのセットアップ手順を説明します。

### 必要な環境
- "Git"&"Github"において、"Git clone"コマンドが実行可能な環境
- プログラミングエディタ (推奨 VScode)
- SSH接続が可能なPc (推奨 Windows 11)
-  LANポート対応Pc (USB to LANでも可能)
### 1. リポジトリのクローン
まず、以下のコマンドを実行し、GitHubリポジトリをローカルにクローンします。
```bash
git clone https://github.com/milky6394/Maizuru_Akebono3.git
cd Maizuru_Akebono3
```
### 2. Python環境の構築とライブラリのインストール
#### Pythonの準備
Python 3.10以上がインストールされていることを確認してください。  
**Caution**PythonはVersion 3.12.6が最も安定して動作します。  
[Python3.12.6](https://www.python.org/downloads/release/python-3126/)

#### 仮想環境の構築
Windowsでは、システムにインストールされている他のPythonライブラリとの競合を避けるため、プロジェクトごとに仮想環境を作成することが強く推奨されます。

以下のコマンドで、プロジェクト用の仮想環境 (`venv`) を作成し、有効化します。
```bash
python -m venv venv
.\venv\Scripts\activate
```
プロンプトの先頭に `(venv)` と表示されれば、仮想環境が有効になっています。

#### ライブラリのインストール
このプロジェクトでは、主に以下のライブラリを使用します。
- **OpenCV (`opencv-python`):** カメラ映像の取得や画像処理に使用します。
- **Pygame (`pygame`):** ゲームパッドやコントローラーからの入力を受け取るために使用します。

リポジトリに含まれる`requirements.txt`ファイルを使って必要ライブラリをインストールします。
```bash
pip install -r requirements.txt
```

#### 3.IPアドレスの固定化
参考サイト  
[【令和最新版】Raspberry Pi を直接WindowsにLanケーブルで接続する際のヘッドレスセットアップ手順](https://zenn.dev/nitic_students/articles/c2228293b4f437)  

ここは結構変えるつもりです

#### [以下に本環境における実行手順を示します(一部不要な点はスキップしています)
Step1.LANケーブルをRaspberryPiとWindowsに直結させる
Step2.microSDを本体に挿入して起動する
Step3.WindowsからPingを飛ばす
**rasp1の場合**
```bash
ping rasp1
```
**rasp2の場合**
```bash
ping rasp2
```
**どちらの機体においても実行可能なコード**
```bash
ping 192.168.50.20
```
Step4.WindowsからPingを飛ばす
```bash
ssh hairobo@rasp1
```
Step5.WindowsでIPを固定する  
**Windows + R**で[ファイル名を指定して実行]を起動
```
ncpa.cpl
```
を実行.  
- イーサネットを選択しプロパティ  
- IPv4のプロパティを開く  
- 任意のIPを割り当て、固定する  
-- DNSサーバは空欄  
-- IPアドレス: 192.168.50.10  
-- サブネットマスク: 255.255.255.0  
-- デフォルトゲートウェイ: 空欄   
-- DNSサーバー: 空欄  
Step6.WindowsのRunからservices.mscを実行する    
詳細は以下サイトを参照してください  
[【令和最新版】Raspberry Pi を直接WindowsにLanケーブルで接続する際のヘッドレスセットアップ手順](https://zenn.dev/nitic_students/articles/c2228293b4f437)  
**Windows + R**で[ファイル名を指定して実行]を起動
```
services.msc
```
Routing and Remote Accessを有効化  
インターネット接続の共有を設定  
詳細は以下サイトを参照してください  
[【令和最新版】Raspberry Pi を直接WindowsにLanケーブルで接続する際のヘッドレスセットアップ手順](https://zenn.dev/nitic_students/articles/c2228293b4f437)  
**Windows + R**で[ファイル名を指定して実行]を起動
```
ncpa.cpl
```
#### Last Steps
1.SSH接続を試行  
**rasp1(Main)の場合**
```bash
ssh hairobo@rasp1
```
**rasp2(Sub)の場合**  
```bash
ssh hairobo@rasp2
```