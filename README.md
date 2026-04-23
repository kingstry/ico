# 桌面图标管理工具 - 使用说明

## 文件清单
- desktop_restore.py   → 主程序代码
- 一键打包.bat         → 双击打包成 exe

## 使用步骤

### 第一步：打包成 exe
1. 确保电脑已安装 Python（https://www.python.org）
   - 安装时必须勾选 "Add Python to PATH"
2. 把 desktop_restore.py 和 一键打包.bat 放在同一个文件夹
3. 双击运行 【一键打包.bat】
4. 等待完成后，exe 文件会出现在 dist 文件夹里

### 第二步：使用程序
1. 把桌面图标摆放到你想要的位置
2. 右键 exe → 以管理员身份运行
3. 点击【保存当前位置】
4. 以后图标乱了，再次运行程序
5. 点击【恢复保存的位置】即可还原

## 注意事项
- 必须以【管理员身份运行】才能读写桌面图标位置
- 位置数据保存在 positions.json 文件里，不要删除它
- 支持 Windows 10 / Windows 11
