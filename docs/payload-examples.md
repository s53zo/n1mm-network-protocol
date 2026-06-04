# Payload Examples

The examples use neutral station names and documentation IP addresses. Replace
them with real LAN values before testing.

## Discovery

```text
N1MMA%192.0.2.10%12070%1.0.11229.0%N0CALL%%
N1MMB%192.0.2.20%12070%1.0.11229.0%N0CALL%vpn-name%
```

## Multi-User TCP Frames

Frame shape:

```text
DATA__<stationNrTwoDigits>%<station>%<command>%<fields...>%~__DATA
```

Command examples:

| Command | Example payload |
| --- | --- |
| `ADDBLACKLISTCALL` | `DATA__00%N1MMA%ADDBLACKLISTCALL%K1BAD%~__DATA` |
| `ADDSPOT` | `DATA__00%N1MMA%ADDSPOT%K1ABC%2026-06-02 12:00:00%1407400%Test spot%1407400%N0CALL%0%~__DATA` |
| `CHECKSUM` | `DATA__00%N1MMA%CHECKSUM%2026-06-02 12:00:00%2026-06-02 13:00:00%123456%CQWPXCW%N0CALL%60%False%False%~__DATA` |
| `CLOSEPORT` | `DATA__00%N1MMA%CLOSEPORT%~__DATA` |
| `CONFIRMED` | `DATA__00%N1MMA%CONFIRMED%2026-06-02 12:00:00%2026-06-02 13:00:00%123456%60%~__DATA` |
| `CONTESTNAME` | `DATA__00%N1MMA%CONTESTNAME%N1MMA%CQWPXCW%%~__DATA` |
| `CQFREQ` | `DATA__00%N1MMA%CQFREQ%1407400%~__DATA` |
| `DELETEQS` | `DATA__00%N1MMA%DELETEQS%2026-06-02 12:00:00%N1MMA%60%~__DATA` |
| `DELETESPOT` | `DATA__00%N1MMA%DELETESPOT%K1ABC%1407400%~__DATA` |
| `DISCONNECT_ME` | `DATA__00%N1MMA%DISCONNECT_ME%~__DATA` |
| `ECHO` | `DATA__00%N1MMA%ECHO%2026-06-02%12:00:00%~__DATA` |
| `ECHOREQ` | `DATA__00%N1MMA%ECHOREQ%2026-06-02%12:00:00%~__DATA` |
| `FILE` | `DATA__00%N1MMA%FILE%Master.scp%K1ABC N0CALL TEST%~__DATA` |
| `FREQ` | `DATA__00%N1MMA%FREQ%1407400%~__DATA` |
| `FREQMODE` | `DATA__00%N1MMA%FREQMODE%1407400%USB%True%~__DATA` |
| `FUNCTIONKEY` | `DATA__00%N1MMA%FUNCTIONKEY%1%K1ABC%1%~__DATA` |
| `IAM` | `DATA__00%N1MMA%IAM% 0%~__DATA` |
| `LASTQAT` | `DATA__00%N1MMA%LASTQAT%2026-06-02 12:00:00%~__DATA` |
| `MASTER` | `DATA__00%N1MMA%MASTER%N1MMA%~__DATA` |
| `PACKET` | `DATA__00%N1MMA%PACKET%DX de N0CALL: 14025.0 K1ABC CW 1200Z%~__DATA` |
| `PACKETSTRING` | `DATA__00%N1MMA%PACKETSTRING%SH/DX K1ABC%~__DATA` |
| `PASSFREQ` | `DATA__00%N1MMA%PASSFREQ%1407400%~__DATA` |
| `QSO` | `DATA__00%N1MMA%QSO%1900-01-01 00:00:00%2026-06-02 12:00:00%K1ABC%14074.00%14074.00%CW%CQWPXCW%599%599%K%N0CALL%%%%001%%%0%5%1001%1%0%0%%14.00%K1%%1%N0CALL%%1%0%%NA%%1%%1%0%N1MMA%1%1%11111111111111111111111111111111%1%~__DATA` |
| `QSODELETE` | `DATA__00%N1MMA%QSODELETE%K1ABC%2026-06-02 12:00:00%~__DATA` |
| `QSONRS` | `DATA__00%N1MMA%QSONRS%CQWPXCW%0%1001%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%0%~__DATA` |
| `REEDITQSO` | `DATA__00%N1MMA%REEDITQSO%2026-06-02 11:59:00%K1OLD%2026-06-02 12:00:00%K1ABC%14074.00%14074.00%CW%CQWPXCW%599%599%K%N0CALL%%%%001%%%0%5%1001%1%0%0%%14.00%K1%%1%N0CALL%%1%0%%NA%%1%%1%0%N1MMA%1%1%11111111111111111111111111111111%1%~__DATA` |
| `REJECTNR` | `DATA__00%N1MMA%REJECTNR%1001%~__DATA` |
| `REMOVECALLSTACKCALLSIGN` | `DATA__00%N1MMA%REMOVECALLSTACKCALLSIGN%K1ABC%~__DATA` |
| `REQCONTESTNAME` | `DATA__00%N1MMA%REQCONTESTNAME%N1MMA%?%~__DATA` |
| `REQCQFREQ` | `DATA__00%N1MMA%REQCQFREQ%~__DATA` |
| `REQPASSFREQ` | `DATA__00%N1MMA%REQPASSFREQ%~__DATA` |
| `RESERVENR` | `DATA__00%N1MMA%ReserveNr%1001%1407400%~__DATA` |
| `RESETQSONRS` | `DATA__00%N1MMA%RESETQSONRS%~__DATA` |
| `RESYNCQSO` | `DATA__00%N1MMA%RESYNCQSO%1900-01-01 00:00:00%2026-06-02 12:00:00%K1ABC%14074.00%14074.00%CW%CQWPXCW%599%599%K%N0CALL%%%%001%%%0%5%1001%1%0%0%%14.00%K1%%1%N0CALL%%1%0%%NA%%1%%1%0%N1MMA%1%1%11111111111111111111111111111111%1%~__DATA` |
| `SKED` | `DATA__00%N1MMA%SKED%11111111-1111-1111-1111-111111111111%CQWPXCW%%False%2026-06-02 12:30:00%K1ABC%14074.0%CW%N1MMA%Test sked%~__DATA` |
| `SKEDD` | `DATA__00%N1MMA%SKEDD%~__DATA` |
| `SKEDSYNC` | `DATA__00%N1MMA%SKEDSYNC%~__DATA` |
| `STACKCALL` | `DATA__00%N1MMA%STACKCALL%2026-06-02 12:00:00%K1ABC%14074.00%14074.00%CW%CQWPXCW%599%599%K%N0CALL%%%%001%%%0%5%1001%1%0%0%%14.00%K1%%1%N0CALL%%1%0%%NA%%1%%1%0%N1MMA%1%1%11111111111111111111111111111111%1%~__DATA` |
| `STACKANOTHERCALL` | `DATA__00%N1MMA%STACKANOTHERCALL%K1ABC%~__DATA` |
| `STATUS` | `DATA__00%N1MMA%STATUS%1407400%1407400%-1%N0CALL%0%0%CW%MULTI-OP%ONE%CN%1.0.11229.0%-1%0%0%0%0%0%~__DATA` |
| `STOPIAM` | `DATA__00%N1MMA%STOPIAM%~__DATA` |
| `TIME` | `DATA__00%N1MMA%TIME%2026-06-02 12:00:00%~__DATA` |
| `TALK` | `DATA__00%N1MMA%TALK%[N1MMA] test message%~__DATA` |
| `WHOAREU` | `DATA__00%N1MMA%WHOAREU%~__DATA` |
| `XMIT` active | `DATA__00%N1MMA%XMIT%-1%F1Virtual%0%0%0%~__DATA` |
| `XMIT` release | `DATA__00%N1MMA%XMIT%0%%0%0%0%~__DATA` |
| `XMIT` forced stop | `DATA__00%N1MMA%XMIT%0%%0%0%-1%~__DATA` |

## Request/Response Examples

Heartbeat:

```text
DATA__00%N1MMA%ECHOREQ%2026-06-02%12:00:00%~__DATA
DATA__00%N1MMB%ECHO%2026-06-02%12:00:00%~__DATA
```

Frequency request:

```text
DATA__00%N1MMA%REQCQFREQ%~__DATA
DATA__00%N1MMB%CQFREQ%1407400%~__DATA
DATA__00%N1MMB%FREQ%1407400%~__DATA
```

Pass frequency request:

```text
DATA__00%N1MMA%REQPASSFREQ%~__DATA
DATA__00%N1MMB%PASSFREQ%1407400%~__DATA
```

IAM stop:

```text
DATA__00%N1MMA%IAM% 0%~__DATA
DATA__00%N1MMB%STOPIAM%~__DATA
```

Checksum confirmation:

```text
DATA__00%N1MMA%CHECKSUM%2026-06-02 12:00:00%2026-06-02 13:00:00%123456%CQWPXCW%N0CALL%60%False%False%~__DATA
DATA__00%N1MMB%CONFIRMED%2026-06-02 12:00:00%2026-06-02 13:00:00%123456%60%~__DATA
```

## UDP 13064 XML Receiver

```xml
<RoverQTH>FN42</RoverQTH>
```

```xml
<radio_setfrequency>
  <app>N1MM</app>
  <frequency>14074.0</frequency>
  <radionr>1</radionr>
  <mousebutton>Left</mousebutton>
</radio_setfrequency>
```

```xml
<RadioCmd Nr="1" Cmd="F1" />
```

```xml
<RCmd>
  <RadioNr>1</RadioNr>
  <RadioCommand>F1</RadioCommand>
  <Zoom>In</Zoom>
</RCmd>
```

```xml
<Spectrum>
  <Name>External SDR</Name>
  <LowScopeFrequency>14000000</LowScopeFrequency>
  <HighScopeFrequency>14100000</HighScopeFrequency>
  <ScalingFactor>1</ScalingFactor>
  <DataCount>4</DataCount>
  <SpectrumData>0,10,8,0</SpectrumData>
</Spectrum>
```

## UDP 12080 CW/Serial Examples

Raw comm-port bridge data uses the first two ASCII characters as a decimal port
number:

```text
01FA00014074000;
```

XML commands:

```xml
<CWControlString>
  <PortNr>1</PortNr>
  <mycall>N0CALL</mycall>
  <callsign>K1ABC</callsign>
  <speed>28</speed>
  <qsonumber>1001</qsonumber>
  <stopit>False</stopit>
  <preventstop>False</preventstop>
</CWControlString>
```

```xml
<CWSendStr>
  <PortNr>1</PortNr>
  <CWString>CQ TEST N0CALL</CWString>
  <Delay>0</Delay>
</CWSendStr>
```

```xml
<SetWPM>
  <PortNr>1</PortNr>
  <Value>28</Value>
</SetWPM>
```

## Rotor Examples

Inbound rotor status on UDP `13010`:

```text
Rotor 1@900
```

Outbound rotor command on UDP `12040`:

```xml
<N1MMRotor>
  <rotor>Rotor 1</rotor>
  <goazi>90.0</goazi>
  <offset>0.0</offset>
  <bidirectional>0</bidirectional>
  <freqband>14.0</freqband>
</N1MMRotor>
```

## External XML Broadcast Examples

```xml
<AppInfo>
  <app>N1MM</app>
  <dbname>CQWPXCW.s3db</dbname>
  <contestnr>1</contestnr>
  <contestname>CQWPXCW</contestname>
  <StationName>N1MMA</StationName>
  <mycall>N0CALL</mycall>
</AppInfo>
```

```xml
<contactinfo>
  <app>N1MM</app>
  <contestname>CQWPXCW</contestname>
  <timestamp>2026-06-02 12:00:00</timestamp>
  <mycall>N0CALL</mycall>
  <call>K1ABC</call>
  <band>14.00</band>
  <mode>CW</mode>
  <snt>599</snt>
  <rcv>599</rcv>
  <StationName>N1MMA</StationName>
</contactinfo>
```

```xml
<spot>
  <app>N1MM</app>
  <StationName>N1MMA</StationName>
  <dxcall>K1ABC</dxcall>
  <frequency>14074</frequency>
  <spottercall>N0CALL</spottercall>
  <timestamp>2026-06-02 12:00:00</timestamp>
  <action>add</action>
  <mode>CW</mode>
  <comment>Test spot</comment>
</spot>
```

Score XML:

```xml
<?xml version="1.0"?>
<dynamicresults>
  <contest>CQ-WPX-CW</contest>
  <call>N0CALL</call>
  <ops>N0CALL</ops>
  <score>3</score>
  <timestamp>2026-06-02 12:00:00</timestamp>
</dynamicresults>
```

## WSJT/JTDX Examples

Plain ADIF import over WSJT/JTDX UDP or external logging TCP:

```text
<call:5>K1ABC <band:3>20M <mode:3>FT8 <qso_date:8>20260602 <time_on:6>120000 <rst_sent:3>-10 <rst_rcvd:3>-08 <eor>
```

Length-prefixed external logging command:

```text
<command:3>Log<parameters:64><call:5>K1ABC <band:3>20M <mode:3>FT8 <qso_date:8>20260602 <eor>
```

WSJT/JTDX radio TCP query/response:

```text
<command:10>CmdGetFreq<parameters:0>
<CmdFreq:9>14.074000
```

```text
<command:12>CmdGetTXFreq<parameters:0>
<CmdTXFreq:9>14.074000
```

Radio TCP set/control commands:

```text
<command:14>CmdSetFreqMode<parameters:15>14074000>DATA-U
<command:10>CmdSetFreq<parameters:8>14074000
<command:12>CmdSetTXFreq<parameters:8>14075000
<command:10>CmdSetMode<parameters:6>DATA-U
<command:8>CmdSplit<parameters:2>ON
<command:11>CmdQSXSplit<parameters:8>14075000
<command:5>CmdRX<parameters:0>
<command:5>CmdTX<parameters:0>
```

JTTY TCP examples:

```text
<RXTEXT:13>CQ K1ABC FN42
<TXTEXT:7>599 001
<XMIT:ON>
<XMIT:OFF>
<OUTPUTCOMPLETE>
<CLOSE>
<ABORT>
```

## MMTTY Special TCP Marker

```text
Server Connected
Client Connected
```

## TCP Radio Examples

TCP radio payloads are radio CAT/control strings, not N1MM DATA frames:

```text
FA00014074000;
##CN;
```
