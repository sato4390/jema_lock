# Home AssistantからJEMAを操作

Home Assistantからパナソニックの[IP/JEM-A変換アダプター](https://www2.panasonic.biz/scvb/a2A/opnItemDetail?contents_view_flg=1&item_cd=HF-JA2-W&item_no=HF-JA2-W&b_cd=501&vcata_flg=1&simple_search_flg=&itmcmp_link_flg=&itmcmp_add_flg=)を介して鍵を操作します。

## インストール方法

このリポジトリの内容をHome Assistantのconfig/custom_components/jema_lockディレクトリにコピーしてください。

## 設定方法

configuration.yamlに次のような設定を追加してください。

```yaml
lock:
  - platform: jema_lock
    name: Lock
    url: http://[変換アダプターのIPアドレス]:8080/
    password: PASSWORD
```