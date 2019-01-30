@echo off
set image=%1

serveus\\detectionfiles\\darknet_no_gpu.exe detector test serveus\\detectionfiles\\plasmodium-obj.data serveus\\detectionfiles\\plasmodium-tinyx.cfg serveus\\detectionfiles\\final.weights serveus\\detectionfiles\\plasmodium/thick/%image% -dont_show -thresh 0.25