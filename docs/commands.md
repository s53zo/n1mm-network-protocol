# Multi-User TCP Commands

Field layouts start after the command name. Every TCP frame also has the
two-digit station number and source station before the command:

```text
DATA__00%<sourceStation>%<command>%<fields...>%~__DATA
```

Boolean values commonly use Visual Basic style: `-1` for true and `0` for
false. Some paths also accept `True` and `False`.

| Command | Fields | Receiver behavior | Response |
| --- | --- | --- | --- |
| `ADDBLACKLISTCALL` | `callsign` | Replaces/updates the bad-spot call list. | None |
| `ADDSPOT` | `call`, `timestamp`, `freq*100`, `comment`, `qsx*100`, `spotter`, `isWorked` | Adds a packet spot. | None |
| `CHECKSUM` | `startTS`, `endTS`, `checksum`, `contest`, `myCall`, `numMinutes`, `resyncAll`, `rescoreRequested` | Compares station log checksum and may start resync repair. | `CONFIRMED` when contest matches |
| `CLOSEPORT` | none | Stops the Telnet client if open. | None |
| `CONFIRMED` | `startTS`, `endTS`, `checksum`, `numMinutes` | Advances checksum/resync windows. | Next `CHECKSUM` until complete |
| `CONTESTNAME` | `station`, `contestName`, `contestSubType` | Stores remote contest context and warns on mismatch. | None |
| `CQFREQ` | `freq*100` | Updates remote CQ/pass frequency and adds a CQ literal spot. | Response to `REQCQFREQ` |
| `DELETEQS` | `startTS`, `stationName`, `numMinutes` | Deletes a time window for checksum repair. | Followed by `RESYNCQSO` records |
| `DELETESPOT` | `callsign`, `freq*100` | Deletes a packet spot. | None |
| `DISCONNECT_ME` | none | Closes/removes the sending station. | None |
| `ECHO` | `date`, `time` | Updates liveness timestamp. | Response to `ECHOREQ` |
| `ECHOREQ` | `date`, `time` | Requests heartbeat response. | `ECHO` with same fields |
| `FILE` | `fileName`, `contents` or file payload shape | Processes synchronized file content. | None |
| `FREQ` | `freq*100` | Updates remote station frequency. | Sent by frequency update paths and `REQCQFREQ`/`WHOAREU` handling |
| `FREQMODE` | `freq*100`, `mode`, `focusBackFlag` | Changes radio frequency/mode for call-stack workflow. | None |
| `FUNCTIONKEY` | `radioNr`, `callsign`, `keyNum` | Activates a radio/window and sends a function key. | None |
| `IAM` | station number text | Announces station identity. | `STOPIAM` |
| `LASTQAT` | last local QSO timestamp | Can start checksum resync if the remote is newer; also sends skeds. | May trigger `CHECKSUM`; sends skeds |
| `MASTER` | `masterStationName` | Marks the current master station. | None |
| `PACKET` | packet text | Low-priority packet/Telnet feed. | None |
| `PACKETSTRING` | packet/Telnet command string | Sends text to the master Telnet client. | None |
| `PASSFREQ` | `freq*100` | Updates pass frequency. | Response to `REQPASSFREQ` |
| `QSO` | `oldTimestamp`, then 43-field `Contact.QSOString()` | Adds/replaces a network QSO. | No explicit ACK |
| `QSODELETE` | `callsign`, `timestamp` | Deletes a matching contact. | None |
| `QSONRS` | `contestName`, `QSONumbers[0..31]` | Merges serial number state by taking max values. | Used for serial conflict correction |
| `REEDITQSO` | `oldTimestamp`, `oldCallsign`, 43-field `Contact.QSOString()` | Replaces an edited network QSO. | No explicit ACK |
| `REJECTNR` | `oldNumber` | Clears a reserved serial number. | None |
| `REMOVECALLSTACKCALLSIGN` | `callsign` | Removes a call from the call stack. | None |
| `REQCONTESTNAME` | `station`, unused token | Requests contest context. | `CONTESTNAME` |
| `REQCQFREQ` | none or ignored token | Requests CQ and current frequency. | `CQFREQ` and `FREQ` |
| `REQPASSFREQ` | none or ignored token | Requests pass frequency. | `PASSFREQ` |
| `RESERVENR` | reserved serial, `freq*100` | Updates or rejects reserved serial state. | Conditional `QSONRS` |
| `RESETQSONRS` | none | Clears serial numbers without rebroadcast. | None |
| `RESYNCQSO` | `oldTimestamp`, 43-field `Contact.QSOString()` | Bulk-upserts a resync QSO. | Completion is via checksum flow |
| `SKED` | `guid`, `contest`, `subtype`, `deleted`, `time`, `call`, `freq`, `mode`, `originStation`, `comment` | Inserts or updates a sked. | None |
| `SKEDD` | none | Deletes skeds for current contest. | None |
| `SKEDSYNC` | none | Requests all skeds. | `SKED` records |
| `STACKCALL` | 43-field `Contact.QSOString()` | Parses and stacks a contact. | None |
| `STACKANOTHERCALL` | `callsign` | Adds a partner call-stack entry. | None |
| `STATUS` | pass/CQ freq, current freq, running flag, operator, last10, last100, mode, operator category, transmitter category, country-file version prefix, app version, block-station, block-band, block-band-mode, force-stop, force-stop-CQ-only, run2 flag | Updates remote station state and warns on mismatches. | None |
| `STOPIAM` | none | Stops repeated `IAM` from a station. | Response to `IAM` |
| `TIME` | UTC timestamp | Syncs or warns about station clock offset. | None |
| `TALK` | message text, often prefixed with `[station]` | Displays a talk/network message. | None |
| `WHOAREU` | none | Requests identity and state. | `IAM`, `ECHOREQ`, `FREQ`, `LASTQAT` |
| `XMIT` | `isXmit`, `functionKeyCaption`, `isRemoteRun2`, `isF1Pressed`, `stopCurrentLocalTransmit` | Updates remote transmit state and may stop local transmit. | None |

## Receiver-Supported Commands With No Current Sender Known

These commands are accepted by receivers, but no current sender path is known:

- `REQCONTESTNAME`
- `SKEDSYNC`
- `WHOAREU`

They should still be parsed and handled by interoperable tools.

## Contact.QSOString Fields

`QSO`, `REEDITQSO`, `RESYNCQSO`, and `STACKCALL` embed contact data. The contact
body has 43 fields:

1. `Timestamp`
2. `CallSign`
3. `Freq`
4. `XmitFrequency`
5. `Mode`
6. `ContestName`
7. `SNT`
8. `RCV`
9. `CountryPrefix`
10. `StationPrefix`
11. `QTH`
12. `Name`
13. `Comment`
14. `NR`
15. `Sect`
16. `Prec`
17. `CK`
18. `ZN`
19. `SentNR`
20. `Points`
21. `IsMultiplier1`
22. `IsMultiplier2`
23. `Power`
24. `Band`
25. `WPXPrefix`
26. `Exchange1`
27. `RadioNr`
28. `Op`
29. `GridSquare`
30. `ContestNR`
31. `IsMultiplier3`
32. `MiscText`
33. `Continent`
34. `ContactType`
35. `Run1Run2`
36. `RoverLocation`
37. `RadioInterfaced`
38. `ContactNetworkedCompNr`
39. `NetBiosName`
40. `IsOriginal` as `1` or `0`
41. `IsRunQSO`
42. `Id` as 32 hex digits
43. `IsClaimedQso`

Command prefixes:

- `QSO`: `oldTimestamp` plus the 43 contact fields.
- `REEDITQSO`: `oldTimestamp`, `oldCallsign`, plus the 43 contact fields.
- `RESYNCQSO`: `oldTimestamp` plus the 43 contact fields.
- `STACKCALL`: only the 43 contact fields.
