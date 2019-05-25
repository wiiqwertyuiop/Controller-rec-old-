sleep(period := 1, Mode := "")
{
	static Frequency, MinSetResolution, PID 		; frequency can't change while computer is on

	if (Mode = "P")				; Precise, but the loop will eat CPU cycles! - use for short time periods
	{
		pBatchLines := A_BatchLines
		SetBatchLines, -1  		;	increase the precision
;		if !PID 
;			PID := DllCall("GetCurrentProcessId")
;		pPiority := DllCall("GetPriorityClass","UInt", hProc := DllCall("OpenProcess","Uint",0x400,"Int",0,"UInt", PID)) 	; have to use 0x400 (PROCESS_QUERY_INFORMATION)
;							, DllCall("CloseHandle","Uint",hProc) 
;		if (pPiority != 0x20)  ;  Normal - I figure if priortiy less than normal increase it to normal for accuracy else if its above normal decrease it, so it doesn't affect other programs as much
;			DllCall("SetPriorityClass","UInt", hProc := DllCall("OpenProcess","Uint",0x200,"Int",0,"UInt",PID), "Uint", 0x20) ; set priority to normal ;have to open a new process handle with 0x200 (PROCESS_SET_INFORMATION)
;							, PriorityAltered := True
		if !Frequency
			DllCall("QueryPerformanceFrequency", "Int64*", Frequency) 	; e.g. 3222744 (/s)
		DllCall("QueryPerformanceCounter", "Int64*", Start)
		Finish := Start + ( Frequency * (period/1000))
		loop 
			DllCall("QueryPerformanceCounter", "Int64*", Current) 		;	eats the cpu
		until (Current >= Finish)
		SetBatchLines, %pBatchLines%
;		if PriorityAltered ; restore original priority
;			DllCall("SetPriorityClass","UInt", hProc := DllCall("OpenProcess","Uint",0x200,"Int",0,"UInt",PID), "Uint", pPiority) ; reset priority 
;				, DllCall("CloseHandle","Uint",hProc) 	

	}
	else if (Mode = "HP" || Mode = "HS" )		; hybrid Precise or hybrid suspend
	{ 											; will sleep the majority of the time using AHKs sleep
		if !Frequency 							; and sleep the remainder using Precise or suspend
			DllCall("QueryPerformanceFrequency", "Int64*", Frequency) 
		DllCall("QueryPerformanceCounter", "Int64*", Start)
		Finish := Start + ( Frequency * (period/1000))
		if (A_BatchLines = -1)
			sleep % period - 15  		; if period is < 15 this will be a nagative number which will simply make AHK check its message queue
		else sleep, % period - 25  		; I picked 25 ms, as AHK sleep is usually accurate to 15 ms, and then added an extra 10 ms in case there was an AHK internal 10ms sleep
		DllCall("QueryPerformanceCounter", "Int64*", Current)
		if (Current < Finish) 						; so there is still a small amount of sleep time left, lets use the precise methods for the remainder
		{
			period := (Finish - Current)*1000 / Frequency ; convert remainder to ms
			if (Mode = "HP")
				sleep(period, "P")
			else sleep(period, "S")
		}
	}

	return
}

Send {c up}
Send {x up}
Send {z up}
Send {s up}
Send {q up}
Send {w up}
Send {d up}
Send {ENTER up}
Send {E up}
Send {R up}
Send {t up}
Send {h up}
Send {g up}
Send {f up}
Send {LEFT up}
Send {RIGHT up}
Send {UP up}
Send {DOWN up}
Send {i up}
Send {k up}
Send {j up}
Send {l up}
Send {LSHIFT up}