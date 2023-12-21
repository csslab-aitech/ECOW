# ECOW
[English🇺🇸](./README.md)

## 概要
ECOW(Evolutionary-computation Competition Opt-command Wrapper)は解の管理機能を持つoptコマンドのPythonラッパーです。<br>

optコマンドは[進化計算コンペティション](https://ec-comp.jpnsec.org/ja)(進化計算学会 実世界ベンチマーク問題分科会開催)で解の送受信に利用します。

ECOWを使用して内部的にoptコマンドを実行することにより、ユーザー名と問題番号の管理、重複した解の送信の抑制、解と結果組一覧のファイル保存が自動化されるため、競技へ集中することができるでしょう。

## デモ
<img src="./docs/images/Tutorial.gif" width= 100%>


## 機能紹介
- opthubへ解の送信・評価値の受信
    - 送信方法
        - 引数に解のリストのみを渡す方法
        - 引数に解のリストとno_wait=Trueを渡す方法

    - 受信方法
        - 返り値としてサーバーからの評価値を得る
        - jsonファイルに保存されたサーバーからの評価値を読み込む(no_wait=Trueの場合)
    
## 便利機能
- 状態の確認
    - オプション`(-s, --status)`をつけて実行

- ヒストリーの表示
    - オプション`(-hi, --history)`をつけて実行

- ヒストリーのJSONフォーマットでの保存
    - オプション`(-hi, --history)`と`(-o ファイル名, --output ファイル名)`をつけて実行
    

## 使用方法
[ドキュメント](https://csslab-aitech.github.io/Compe_module/)を参照してください。

## セットアップ
- `python`のインストールが必要です。(3.10動作確認済み)
- モジュールのインストールが必要です
    - `pip install filelock`


## ライセンス
- The MIT License (MIT)
- [ライセンス](./LICENSE)をご覧ください。

## コンタクト
- csslab _at_ aitech.ac.jp (_at_の部分を@に置き換えてください)




