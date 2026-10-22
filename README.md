# TTPlayerRes

千千静听 5.7.9 `ttpres.dll` 的独立资源重建工程，采用 **原版资源基准 + 重建版扩展资源**。适用于原版播放器与 TTPlayerRebuild，提供同一份 x86 DLL。

## 构建

需要 Visual Studio 2026 C++ 工具、Windows SDK、CMake 3.24+、Python 3 和 PowerShell；不需要 VC-LTL、YY-Thunks 或第三方库。

```powershell
./build.ps1 -Package
# 指定与 Action 一致的日期版本：
./build.ps1 -Package -PackageVersion 2026.10.13p1
```

输出到 `build/Release`：

- `ttpres.dll`：无代码、无入口、无导入与导出的资源库，子系统版本 5.01；已恢复原版要求的 DOS 头自定义校验。
- `ttpres-版本号.zip`：只有 `ttpres.dll` 和 DLL 的 `SHA256SUMS.txt`。
- `SHA256SUMS.txt`：ZIP 的校验值。
- `ttpres-component.json`：构建审计记录，供本地检查；不装入 ZIP。

关闭播放器后，把 DLL 放到 **播放器主目录**。不要放入 `AddIn`。原版 `VERSION/1` 保留 5.7.9.0；本项目构建日期记录于 `TTPLAYER_RES_BUILD` 扩展资源及 ZIP 名称。

## 源码布局

| 路径 | 用途 |
| --- | --- |
| `resources/original/manifest.json` | 原版 192 项资源的类型、编号、语言、大小与 SHA-256 |
| `resources/original/menus` | 25 个菜单，保留命令编号、占位项与顺序 |
| `resources/original/dialogs` | 49 个 DIALOGEX、677 个控件及字体、样式、DLU 布局 |
| `resources/original/strings` | 74 个字符串块，含空槽位与分隔符 |
| `resources/original/toolbars` | 4 个工具栏的尺寸与命令顺序 |
| `resources/original/bitmaps` | 标准 BMP，编译时去除文件头还原 DIB |
| `resources/original/skins` | 默认皮肤与下载皮肤的独立 ZIP、XML 和图片目录 |
| `resources/original/raw` | 图标、光标、分组、HTML 和原版版本资源的无损数据 |
| `resources/extended/player.rc` | 重建版新增对话框和字符串的规范 RC 源码 |
| `sdk` | 扩展编号和宿主选择资源的接口 |
| `tools` | 无第三方 Python 依赖的资源编译、审计、SDK 导出和打包工具 |

原版菜单、对话框使用可编辑 UTF-8 JSON，而非有损反编译 RC；构建器精确保留 DIALOGEX 字体 weight/charset、控件 ID、创建数据、对齐填充等细节，再生成标准 `.res`。常规构建拒绝改变原版基准；校验基准后，仅将版本资源的 `CompanyName` 改为 `Sonic853`。审计会还原这一字段并校验整项原版资源，其余 191 项原版资源逐字节保持一致；也兼容此前未修改公司名称的发行包。新增界面请编辑扩展 RC，并在 SDK 中声明范围，避免改坏原版宿主依赖的编号和菜单位置。

完整构建不读取父目录的 DLL、逆向材料或测试代码。首次提取工具 `tools/import_original.py` 仅用于从指定 SHA-256 的原版 DLL 重现基准源码，目标必须为空。

## Action 与播放器接入

独立仓库：<https://github.com/TTPlayerRebuild/TTPlayerRes>。

`Build player resources` 工作流支持 **Release a Version**；沿用北京时间日期和同日 `pN` 后缀，先分配版本再构建。Action 只编译、检查资源契约及打包，不执行测试。

更新宿主 SDK：

```powershell
python tools/export_sdk.py ../rebuild/third_party/ttpres-sdk
```

播放器 Action 默认下载本仓库最新正式 Release，校验 GitHub ZIP 摘要、包内 DLL 摘要、全部原版资源以及扩展 ABI，再将 DLL 打入播放器 ZIP。本仓库首次正式 Release 需先发布，播放器 Action 才能下载；不会静默退回修改版 DLL。

本地播放器设置 `TTPLAYER_STAGE_RUNTIME=ON` 时，使用 `../ttpres/build/Release/ttpres.dll`；可用 `TTPLAYER_TTPRES_DLL` 指定另一份经审计的构建结果。

重建版播放器必须使用包含完整扩展资源的本 DLL，EXE 不内嵌扩展对话框或备用字符串，也不回退到原版 DLL。启动时检查 ABI、9 个对话框和 48 条已分配字符串；缺失、不兼容或不完整时提示更换完整发行包。SDK 只导出编号、加载契约和审计工具，不导出供 EXE 编译的 RC。原版播放器仍可使用本 DLL 的原版资源区。

详见 [实现与验证记录](docs/RECONSTRUCTION_20261013.md)。测试源码与二进制证据保存在相邻播放器的私有 `rebuild/tests/ttpres_audit_20261013`，不上传本仓库、不进入 Action 或发行包。
