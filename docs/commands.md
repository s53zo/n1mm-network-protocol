# Multi-User TCP Commands

Field layouts start after the command name. Every TCP frame also has the
two-digit station number and source station before the command:

```text
DATA__00%<sourceStation>%<command>%<fields...>%~__DATA
```

The command dispatcher and the 43-field contact serializer were checked in
`N1MMLogger.net.exe` versions `1.0.11364.0` and `1.0.11469.0`. The compared
`MultiStation.DataArrivalProcessing` and `Contact.QSOString` methods produce
identical decompiler output in these versions. This is static evidence, not a
live interoperability test; see [the verification record](evidence.md).

Boolean values commonly use Visual Basic style: `-1` for true and `0` for
false. Some paths also accept `True` and `False`.

| Command | Fields | Receiver behavior | Response |
| --- | --- | --- | --- |
| `ADDBLACKLISTCALL` | `callsign` | Replaces/updates the bad-spot call list. | None |
| `ADDSPOT` | `call`, `timestamp`, `freq*100`, `comment`, `qsx*100`, `spotter`, `isWorked` | Adds a packet spot. | None |
| `CHECKSUM` | `startTS`, `endTS`, `checksum`, `contest`, `myCall`, `numMinutes`, `resyncAll`, `rescoreRequested` | Compares station log checksum and may start resync repair when logging QSOs at all stations is enabled. | `CONFIRMED` when that setting is enabled and contest matches |
| `CLOSEPORT` | none | Stops the Telnet client if open. | None |
| `CONFIRMED` | `startTS`, `endTS`, `checksum`, `numMinutes` | Advances checksum/resync windows. | Next `CHECKSUM` until complete |
| `CONTESTNAME` | `station`, `contestName`, `contestSubType` | Stores remote contest context and warns on mismatch. | None |
| `CQFREQ` | `freq*100` | Updates remote CQ/pass frequency and adds a CQ literal spot. | Response to `REQCQFREQ` |
| `DELETEQS` | `startTS`, `stationName`, `numMinutes` | Deletes non-original copies for the named station in a half-open time window, subject to the QSO compatibility gate. | Followed by `RESYNCQSO` records in the repair flow |
| `DELETESPOT` | `callsign`, `freq*100` | Deletes a packet spot. | None |
| `DISCONNECT_ME` | none | Closes/removes the sending station. | None |
| `ECHO` | `date`, `time` | Updates liveness timestamp. | Response to `ECHOREQ` |
| `ECHOREQ` | `date`, `time` | Requests heartbeat response. | `ECHO` with same fields |
| `FILE` | `fileName`, `contents` for the supported two-field form | Writes recognized `wl_cty.dat` or `Master.scp` content and reloads the corresponding data. Generic sender form is inconsistent; see below. | None |
| `FREQ` | `freq*100` | Updates remote station frequency. | Sent by frequency update paths and `REQCQFREQ`/`WHOAREU` handling |
| `FREQMODE` | `freq*100`, `mode`, `focusBackFlag` | Changes radio frequency/mode for call-stack workflow. | None |
| `FUNCTIONKEY` | `radioNr`, `callsign`, `keyNum` | Activates a radio/window and sends a function key. | None |
| `IAM` | station number text | Announces station identity. | `STOPIAM` |
| `LASTQAT` | last local QSO timestamp | Can start checksum resync if the remote is newer and the local log is nonempty; always sends skeds. | May trigger `CHECKSUM`; broadcasts `SKED` records |
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
| `REQCONTESTNAME` | two consumed but unused tokens | Requests contest context. | Targeted `CONTESTNAME`; inner station field is the requester name |
| `REQCQFREQ` | none or ignored token | Requests CQ and current frequency. | Broadcasts `CQFREQ` and `FREQ` |
| `REQPASSFREQ` | none or ignored token | Requests pass frequency. | Broadcasts `PASSFREQ` |
| `RESERVENR` | reserved serial, `freq*100` | Updates or rejects reserved serial state. | Conditional `QSONRS` |
| `RESETQSONRS` | none | Clears serial numbers without rebroadcast. | None |
| `RESYNCQSO` | `oldTimestamp`, 43-field `Contact.QSOString()` | Bulk-upserts a resync QSO. | Completion is via checksum flow |
| `SKED` | `guid`, `contest`, `subtype`, `deleted`, `time`, `call`, `freq`, `mode`, `originStation`, `comment` | Inserts or updates a sked by GUID; receiver consumes but does not store subtype. | None |
| `SKEDD` | none | Deletes skeds for current contest. | None |
| `SKEDSYNC` | none | Requests skeds for the current contest name. | Broadcasts `SKED` records |
| `STACKCALL` | 43-field `Contact.QSOString()` | Parses and stacks a contact. | None |
| `STACKANOTHERCALL` | `callsign` | Adds a partner call-stack entry. | None |
| `STATUS` | pass/CQ freq, current freq, running flag, operator, last10, last100, mode, operator category, transmitter category, country-file version prefix, app version, block-station, block-band, block-band-mode, force-stop, force-stop-CQ-only, run2 flag | Updates remote station state and warns on mismatches. | None |
| `STOPIAM` | none | Stops repeated `IAM` from a station. | Response to `IAM` |
| `TIME` | UTC timestamp | Syncs or warns about station clock offset. | None |
| `TALK` | message text, often prefixed with `[station]` | Displays a talk/network message. | None |
| `WHOAREU` | none | Requests identity and state. | Targeted `IAM` and `LASTQAT`; broadcasts `ECHOREQ` and `FREQ` |
| `XMIT` | `isXmit`, `functionKeyCaption`, `isRemoteRun2`, `isF1Pressed`, `stopCurrentLocalTransmit` | Updates remote transmit state and may stop local transmit. | None |

## Receiver-Supported Commands With No Current Sender Known

These commands are accepted by receivers. No sender was found in the inspected
`MultiOpManager` sender methods or networking class string searches in either
version; this bounded search does not prove that no sender exists elsewhere:

- `REQCONTESTNAME`
- `SKEDSYNC`
- `WHOAREU`

They should still be parsed and handled by interoperable tools.

## Compatibility and Response Details

`QSO`, `REEDITQSO`, `RESYNCQSO`, `QSODELETE`, and `DELETEQS` call
`MultiStation.IsOkToStoreQSO` before changing the log. It requires an exact
application-version match and a matching contest name. If both sides use
`QSOPARTY`, their subtypes must match. The remote contest name `STARTING` bypasses
the contest-name/subtype tests, but not the version test. `NewLogQSO` also checks
the contest name inside each contact record before storing it.

Normal `SendStatus` broadcasts `CONTESTNAME` followed by `STATUS`. Its
`CONTESTNAME` inner station name is the sender; the receiver-only
`REQCONTESTNAME` handler instead puts the requester's station name there. Both
request tokens are ignored. Preserve the final empty subtype field: the receiver
expects three fields plus the trailing delimiter.

Frequency replies use the ordinary broadcast senders. `WHOAREU` sends its `IAM`
and `LASTQAT` directly to the requesting station, while its `ECHOREQ` and `FREQ`
use broadcast senders. `SendFreq` uses active-radio frequency in `WHOAREU` and
split/transmit frequency in `REQCQFREQ`.

`FREQMODE` consumes its focus flag as text and compares it with case-sensitive
`True`/`False` strings in the default receiver path. Do not substitute `-1`/`0`
for this particular field. This command also contains callsign-specific radio
selection paths; it is not a generic radio-control API.

`FILE` has no general escaping or chunking scheme. `SendFile` explicitly emits
`FILE%Master.scp%<contents>%` for the master callsign file. Its other branch emits
file contents without explicitly adding the filename, although the receiver
consumes filename and contents as separate tokens. Treat that branch as an
implementation inconsistency rather than a proven generic transfer format.

## Checksum and Log Repair

The following static behavior is the same in the compared methods in both
versions (`MultiStation.DataArrivalProcessing`, `DBSupport.SetOfQs`,
`ComputeCheckSum`, `SendQs`, `DeleteQsFor`, and `CRC32Module.CRC32`):

1. `LASTQAT` compares the peer's advertised last QSO time with local copies of
   that peer's contacts. A newer peer can initiate repair when the local log
   already contains contacts; automatic repair is suppressed for an empty log.
2. A `CHECKSUM` identifies a start time, an overall end time and a window length
   in minutes. `SetOfQs` selects the named station's records in the current
   contest instance with `start <= TS < start + numMinutes`, ordered by timestamp
   and callsign. The overall `endTS` does not bound this individual SQL window.
3. The receiver processes repair only with `IsLogQsAtAllStations` enabled.
   A callsign mismatch emits a warning but does not itself prevent repair;
   a contest-name mismatch prevents repair and confirmation. `resyncAll` starts
   checks with other stations. `rescoreRequested` sets the rescore request flag.
4. On mismatch the receiver sends `DELETEQS` naming its own station, then sends
   its selected own-station records as `RESYNCQSO`, then `CONFIRMED` with its
   checksum. `DeleteQsFor` removes only `IsOriginal=0` copies for that named
   station, within the half-open window, in the current contest or deleted-QSO
   records (`ContestNr=-1`).
5. `CONFIRMED` compares the repaired peer copies, records success/failure, advances
   the start by `numMinutes`, and sends another `CHECKSUM`. Completion is declared
   when a received confirmation has `startTS > endTS`, not when they are equal.

The checksum is a signed 32-bit CRC, not a sum of the wire contact strings.
`ComputeCheckSum` concatenates database-column text without separators, beginning
with the formatted timestamp, then walks the explicit `SetOfQs` select order.
It skips `CountryPrefix`, `Points`, `IsMultiplier1`, `IsMultiplier2`,
`IsMultiplier3`, `WPXPrefix`, `Continent`, and `IsOriginal`. `ContestNr` contributes
only `-1` for a deleted record; normal local contest numbers are omitted.
`CRC32Module` starts at all ones, uses the reflected CRC-32 table, and XORs all
ones at the end. It consumes Visual Basic `Asc` character values rather than
UTF-8 bytes and returns signed decimal text on the wire. Locale-sensitive
conversions mean an independent implementation needs explicit non-ASCII and
numeric-format checks; the Python examples do not implement log repair.

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

The contact frequencies (`Freq`, `XmitFrequency`) are decimal kHz and `Band` is
in MHz; these are not the integer `kHz * 100` fields used by station-state
commands. Selected free-text contact fields replace `%` with `!` before
serialization: SNT, RCV, QTH, Name, Comment, Sect, Power, and Exchange1. The outer
frame sender separately replaces `~` with `!`. There is no inverse unescaping.

On receive, `SetNewContact` remaps a non-deleted `ContestNR` to the local current
contest instance and clears `IsOriginal` when `NetBiosName` is another computer.
Network upsert matching in `NewLogQSO` uses timestamp, station name, and callsign;
the GUID field is carried but is not the lookup key in that method.

Do not substitute the separate legacy `MultiOpManager.QSOString(Contact)`
helper: it has a shorter, differently ordered layout. The network QSO, re-edit,
resync, and stack senders inspected here call `Contact.QSOString()`.
