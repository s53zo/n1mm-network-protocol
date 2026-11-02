# Adjacent Networking Interfaces

These notes describe static code paths in `N1MMLogger.net.exe` versions
`1.0.11364.0` and `1.0.11469.0`, extracted from the supplied full and update
installers. They do not establish that a feature was enabled or exercised.
The multi-user `DATA__` protocol is separate from all formats below.

## UDP XML and CW/Serial Control

`N1MMInterface.Initialize` creates the UDP `13064` receiver.
`HandleUDPMessage` decodes incoming bytes as ASCII and selects XML element
names case-sensitively:

| Root | Interpretation |
| --- | --- |
| `RoverQTH` | Changes the rover location. |
| `radio_setfrequency` | Reads `frequency` in kHz, `radionr`, and optional `mousebutton`. `Right` switches the target radio and leaves it inactive. |
| `RadioInfo` | Reads `Freq` divided by 100 and `RadioNr`; packets from loopback or the local IP are ignored to avoid following the local broadcast. |
| `RadioCmd`, `RCmd` | Accepts attributes `Nr`/`Cmd`, or child elements `RadioNr`/`RadioCommand`. Radio number zero selects the active window. Remote `Zoom` messages raise the spectrum zoom event; local ones do not. |
| `Spectrum` | Reads `Name`, scope frequency bounds, scaling, count, and CSV data. Routes data to a matching spectrum source; `ZoomIndex` is consumed without applying it in this handler. |

Do not assume every root has identical self-message filtering. Only the
`RadioInfo` and `Zoom` paths above explicitly test the source IP here.

`UDPClass` independently listens on UDP `12080`. It decodes the packet as ASCII.
XML roots include `CWControlString`, `CWSendStr`, `SetBufPTT`, and `SendCW`;
other command roots use `PortNr` and `Value`. The raw bridge path interprets
the first two ASCII characters as a decimal port number and takes the text
from the third character onward as the output string. It also passes the
original byte array to its output event, so the byte-array argument is not a
copy with the two-character header removed.

The broadcast settings and port defaults are listed in [ports.md](ports.md).
`DestinationIPs` and the `Broadcast*Addr` overrides are space-separated lists;
spectrum relay and SDR server lists are comma-separated. `Use_Default` is a
literal option, not an IP address. These paths use datagrams without `DATA__`
framing or a general acknowledgment.

## Rotor

`RotorManager` binds UDP `13010` and parses ASCII `description@heading`.
The numeric heading is in tenths of a degree: `Rotor 1@900` displays 90 degrees.
A heading ending in `?`, or a nonnumeric heading, is not applied.

`N1MMInterface.NewGoAzi` sends `N1MMRotor` XML containing `rotor`, `goazi`,
`offset`, `bidirectional`, and `freqband`. The azimuth/offset are formatted with
one decimal place, and the bidirectional flag is `0` or `1`. The default route
uses `DestinationIPs` and `RotorStartPort` (`12040`); explicit rotor destinations
use their own `ip:port`. `NewStopRotor` uses a `stop` child under `N1MMRotor`.

The companion `N1MMRotor.Net.exe` receiver (`RotorForm.HandleRotorXML`)
binds the rotor manager's start port, initially `12040`, and decodes ASCII.
It selects a rotor by description, numeric port number, or the selected rotor
when the name is empty or `*`. Its direct `N1MMRotor` branch handles `goazi`,
`rotor`, `offset`, `bidirectional`, `stop`, `hwnd`, and `stopprogram`. It scans
only direct children: the logger's nested `stop` payload does not expose its
inner `rotor` to this branch. This asymmetry is visible statically; actual stop
behavior was not tested. `RotorForm.positionfor` reports `description @ heading`
with heading multiplied by ten to UDP `13010` at the configured, space-separated
`RotorReportingIP` addresses (default `127.0.0.1`).

## Spectrum and SDR Server

`AbstractSpectrumProcessing.GetBroadcastDataString` produces `Spectrum` XML
with `Name`, `LowScopeFrequency`, `HighScopeFrequency`, `ScalingFactor`,
`DataCount`, and `SpectrumData`. Relay destinations default to UDP `13064`
when the comma-separated address entry omits a port.

`WaterfallBandmapSpectrumProcessing.SendSpectrumCmd` sends to UDP `13065`
unless an address specifies another port or `AssignedPort` overrides it.
`GetExtIOParms` produces the `SpectrumCmd` root with `Frequency`, `RadioNr`,
`DisplayBins`, `DLLName`, `FrequencyBins`, `ZoomIn`, `ZoomOut`, `RefLevel`, and
`ZoomIndex`. A spectrum window can have an assigned server port; `13065` is
not a fixed port for every window.

The companion `N1MMSDRServer.exe` has a matching `UDPHandler`: its default
receive port is `13065`, overridden by the passed port. It decodes ASCII
`SpectrumCmd` XML and forwards the fields above plus the source IP to its
message event. `SDRServer.GetBroadcastDataString` returns `Spectrum` data with
the same fields as the logger relay plus `ZoomIndex`; return data defaults to
UDP `13064`. Server launch/close paths were inspected statically only; the
server was not started.

## WSJT/JTDX UDP and External Logging TCP

`WSJTCode.Initialize` selects configurable UDP reader and TCP logging addresses
and ports for each interface. `StartWSJTUDPMessageListener` also binds a separate
messenger socket on local UDP `2240` or `2241`. Outgoing messages use the remote
endpoint learned from received UDP, rather than targeting port `2240`/`2241`.

The UDP receiver recognizes three distinct payload families:

- A `Log` command with a `<parameters:N>` length followed by ADIF text.
- Plain ADIF containing both `<call:` and `<eor>` (case-insensitive checks).
- WSJT binary messages, beginning with magic `0xADBCCBDA` (first byte `0xAD`).
  The listener's ASCII-decoded text begins with the replacement character `?`,
  which it uses to select the binary path; `?` is not the first wire byte.
  `processMsg` checks the raw magic, reads schema, message type and ID, and
  dispatches selected types.

`WSJTCode.LoggingTCPListening` accepts the first two text families over TCP.
For framed `Log` it writes the literal ASCII bytes `ACK` before invoking ADIF
import. The plain ADIF branch has no corresponding write. `ACK` is therefore
not proof that a contact was successfully validated and saved.

The inspected logging TCP code processes each read as a text message and uses
the rightmost declared number of characters for the parameter body. It does
not establish a general buffer for fragmented or coalesced length-prefixed
messages. A declared length must include the complete parameter text; these
ADIF-style tags are not XML.

## WSJT/JTDX Radio TCP

`WSJTRadio` creates loopback listeners on `52002` and, for the second radio in
SO2R operation, `52004`. The transport helper forwards ASCII receive chunks to
the command processor. This protocol uses `<command:N>` and `<parameters:N>`
records, not `DATA__` frames.

Frequency values passed to `RadioInterface` are in kHz. `CmdGetFreq` and
`CmdGetTXFreq` format their replies with invariant `N03`, including thousands
separators and three decimal places. At 14.074 MHz the response is therefore:

```text
<CmdFreq:10>14,074.000
<CmdTXFreq:10>14,074.000
```

Set commands parse tagged parameter bodies. A bare numeric parameter is not
equivalent to the tagged body: the handler splits on `>` and reads the value
following an inner tag. `CmdSetFreqMode` expects frequency, mode and a final
split flag in order. `CmdSplit` tests lowercase `on` and `off`, although its
reported split-state text uses uppercase `ON`/`OFF`. The tag names in reconstructed
examples are illustrative where the handler only reads positional values.
See [payload examples](payload-examples.md).

The command processor explicitly splits concatenated records at `<command`,
but the inspected transport does not buffer a partial record across callbacks.
Successful static reconstruction does not demonstrate tolerance of arbitrary
TCP segmentation.

## JTTY and MMTTY

JTTY uses separate loopback listeners on `61002`/`61004`, passed to the external
program with `--n1mm-tcp-port`. `WSJTRadio.ParseTcpMessage` accepts length-prefixed
`RXTEXT`/`TXTEXT` and exact control markers such as `<XMIT:ON>`, `<XMIT:OFF>`,
`<OUTPUTCOMPLETE>`, `<CLOSE>`, and `<ABORT>`. These are receive-side markers;
the application also sends forms such as `<CLOSE:0>` with CRLF. Do not conflate
the two directions. The parser is called on individual receive chunks and does
not establish a full stream reassembly protocol.

`DigitalInterface.ProcessMMTTYData` contains the exact `Server Connected` to
`Client Connected` reply. A listener setup for the previously documented
`52301`/`52303` ports was not established in the selected classes of either
supplied build. The marker handler alone does not establish an active listener
or a generally available MMTTY interface.

## Observed Version Differences

The following differences are visible in the selected recovered methods:

| Area | `1.0.11364.0` | `1.0.11469.0` |
| --- | --- | --- |
| Incoming `Spectrum` source matching | Case-sensitive `SourceName` comparison. | `OrdinalIgnoreCase` comparison. |
| JTTY parser | No `CALLSIGN` branch. | Accepts `<CALLSIGN:N>text` and applies a nonempty callsign to the corresponding entry window. |
| WSJT UDP status in JTTY mode | Applies `DXCall` directly. | Interface 1 tracks callsign transitions; interface 2 ignores empty `DXCall` in this path. |
| SDR display-rate constructor default | `MaxAllowedDisplayRate = 10`. | `MaxAllowedDisplayRate = 40`. |
| SDR process shutdown | Kills the process. | Attempts window close, waits up to two seconds, then kills if still running. |
| Tailscale executable lookup | Hardcoded Program Files path. | Searches common Program Files locations and `PATH`, caching the result. |

The selected decompiled `UDPClass`, `RotorManager`, `TCPRadio`,
`AsyncTcpClient`, `AsyncTcpListener`, and
`WaterfallBandmapSpectrumProcessing` outputs are textually identical between
these builds. This comparison does not prove equality of their dependencies,
external programs, runtime settings, or every networking path in the application.
