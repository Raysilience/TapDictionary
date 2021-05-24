## **Magic Finger Usage**
### 使用前操作
1. 根目录创建 `data/` 文件夹，并导入 `.mdd` 或者 `.mdx` 格式词库
2. 配置 `template.config` 文件并修改文件命名为 `magic_finger.config`
   - access token需要在百度注册账号后获取
   - 字典路径配置为 ./data/***.mdx

### 开始使用 **magic_finger sdk**
  ```python
  # 设置被检测图片路径
  image_path = ''
  # 创建 magic_finger 实例
  mf = magic_finger()
  # 导入被检测图片
  mf.set_image(image_path)
  # 输出检测结果
  result = mf.translate()
  # pc端模拟交互
  mf.draw(mode=mf.DRAWLINE | mf.INTERACTIVE)
```
### demo 展示
```shell
python main.py -f 1.jpg
```
![image](https://github.com/ruizhang95/ocr/blob/main/demo.gif)
