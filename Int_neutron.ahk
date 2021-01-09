#NoEnv
#Persistent
#UseHook
#Singleinstance Force
#include csv.ahk
#include autoUtil.ahk
SetKeyDelay, 10, 50

Tail(k,file)   ; Return the last k lines of file
{
   Loop Read, %file%
   {
      i := Mod(A_Index,k)
      L%i% = %A_LoopReadLine%
   }
   L := L%i%
   Loop % k-1
   {
      IfLess i,1, SetEnv i,%k%
      i--      ; Mod does not work here
      L := L%i% "`n" L
   }
   Return L
}

Loop{
FileSelectFile, Name,,,,*.csv	; wait for csv file to be selected
if (Name)
	break
}

Gui, Add, Text, w400 h26 x20 y20, % "Route: " sys[1] " to " sys[sys.MaxIndex()] " | " hops " jumps"
Gui, Add, Text, w50 h26 xp+500, Fuel:
Gui, Add, Edit, vFuelTank w50 h26 xp+50, 0

Gui, Add, Groupbox, x20 y60 w600 h150, Status
Gui, Add, Text, w300 h26 xp+20 yp+52, Current System: 

Gui, Add, Text, vPrevDisp w300 h26 xp+180 yp-26 c999999, % sys[0]
Gui, Add, Text, vCurrDisp w300 h26 yp+26, % sys[1]
Gui, Add, Text, vNextDisp w300 h26 yp+26 c999999, % sys[2]
Gui, Add, Text, vMoreDisp w300 h26 yp+26 ccccccc, % sys[3]

Gui, Add, Text, vTimeDisp w100 h26 x500 y112, 00:00

Gui, Add, Groupbox, x20 y250 w600 h200, Controls
Gui, Add, Button, w90 h170 gStart xp+500 yp+20, Start

Gui, Show,, FCA

return

GuiClose:
ExitApp