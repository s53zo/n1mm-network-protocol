# Ports and Options

## Port Matrix

| Port | Protocol | Direction | Purpose | Configurability |
| ---: | --- | --- | --- | --- |
| `12070` | TCP | inbound and outbound | Multi-user station synchronization, `DATA__...__DATA` frames. | Local listener is fixed on `12070`; peer port normally defaults to `12070`, with station-specific overrides possible. |
| `12070` | UDP | inbound and outbound | Multi-user discovery advertisements. | Uses the advertised station port, normally `12070`. |
| `12060` | UDP | outbound | Default external XML broadcast destination for radio/app/contact/lookup/spots. | General destination IPs and port, with per-stream address overrides. |
| `12050` | UDP | outbound | Default score-reporting UDP destination. | Score-reporting destination settings and score address overrides. |
| `12040` | UDP | outbound | Default N1MM Rotor command destination. | Rotor start port and rotor address list. |
| `12080` | UDP | inbound | CW/serial/control XML and raw comm-port bridge. | Fixed listener. |
| `13010` | UDP | inbound | Rotor heading status strings. | Fixed listener. |
| `13064` | UDP | inbound | Local radio/spectrum/control XML receiver. | Fixed listener. |
| `13064` | UDP | outbound | Default spectrum-data relay destination when no relay port is supplied. | Spectrum relay address list accepts `ip` or `ip:port`. |
| `13065` | UDP | outbound | Default SDR server command destination for `SpectrumCmd`. | SDR server address accepts `ip` or `ip:port`; assigned SDR ports can override. |
| `2237` | UDP | inbound | WSJT/JTDX message reader for radio/interface 1. | WSJT/JTDX UDP settings. |
| `2239` | UDP | inbound | WSJT/JTDX message reader for radio/interface 2. | WSJT/JTDX UDP settings. |
| `2240` | UDP | local/outbound helper | WSJT/JTDX messenger socket for interface 1. | Fixed. |
| `2241` | UDP | local/outbound helper | WSJT/JTDX messenger socket for interface 2. | Fixed. |
| `52001` | TCP | inbound | External logging TCP listener for WSJT/JTDX interface 1. | Configurable IP/port and enable setting. |
| `52006` | TCP | inbound | External logging TCP listener for WSJT/JTDX interface 2. | Configurable IP/port and enable setting. |
| `52002` | TCP | inbound | WSJT/JTDX radio-control listener for radio 1. | Fixed loopback listener. |
| `52004` | TCP | inbound | WSJT/JTDX radio-control listener for radio 2. | Fixed loopback listener. |
| `61002` | TCP | inbound | WSJT/JTDX JTTY mode listener for radio 1. | Fixed loopback listener, passed to WSJT/JTDX as `--n1mm-tcp-port 61002`. |
| `61004` | TCP | inbound | WSJT/JTDX JTTY mode listener for radio 2. | Fixed loopback listener, passed to WSJT/JTDX as `--n1mm-tcp-port 61004`. |
| `52301` | TCP | inbound | MMTTY special-case external listener for interface 1. | Fixed loopback listener behind a callsign-specific path. |
| `52303` | TCP | inbound | MMTTY special-case external listener for interface 2. | Fixed loopback listener behind a callsign-specific path. |
| user value | TCP | outbound | TCP radio CAT/control connection. | Radio TCP address must be `host:port`; port is validated as `0..65535`. |
| `12099` | n/a | none known | `MultiBroadcastPort` property value. | No listener/sender use is known. |

## External Broadcast Options

Common booleans:

| Setting | Default | Enables |
| --- | --- | --- |
| `IsBroadcastRadio` | `False` | `RadioInfo` UDP broadcast |
| `IsBroadcastAppInfo` | `False` | `AppInfo` UDP broadcast |
| `IsBroadcastContact` | `False` | `contactinfo`, `contactreplace`, `contactdelete` broadcast |
| `IsBroadcastExternalLookup` | `False` | `lookupinfo` broadcast |
| `IsBroadcastScore` | `False` | score reporting timer/posting path |
| `IsBroadcastScoreUDP` | `False` | score XML UDP broadcast |
| `IsBroadcastSpots` | `False` | `spot` XML broadcast |
| `IsBroadcastAllQsos` | `False` | include all network QSOs in contact/score paths |
| `IsBroadcastRotorCommands` | `False` | rotor command broadcast option flag |

Destination settings:

| Setting | Default | Applies to |
| --- | --- | --- |
| `DestinationIPs` | `127.0.0.1` | General destination list for radio/app/contact/lookup/spots |
| `DestinationPort` | `12060` | General UDP destination port |
| `BroadcastRadioAddr` | `Use_Default` | Radio XML destination override |
| `BroadcastAppAddr` | `Use_Default` | App info destination override |
| `BroadcastContactAddr` | `Use_Default` | Contact XML destination override |
| `BroadcastExternalLookupAddr` | `Use_Default` | Lookup XML destination override |
| `BroadcastSpotsAddr` | `Use_Default` | Spot XML destination override |
| `BroadcastScoreAddr` | `Use_Default` | Score UDP destination override |
| `BroadcastRotorAddr` | `Use_Default` | Rotor command destination override |
| `RotorStartPort` | `12040` | Default rotor command destination port |

Explicit broadcast addresses are normally written as `ip:port`. Most streams use
`DestinationIPs:DestinationPort` when their `Broadcast*Addr` is `Use_Default`.
Score UDP defaults to `127.0.0.1:12050` through score-reporting settings.

## Inbound XML Roots

UDP `13064` accepts:

- `RoverQTH`
- `radio_setfrequency`
- `RadioInfo`
- `RadioCmd`
- `RCmd`
- `Spectrum`

UDP `12080` accepts special XML roots:

- `CWControlString`
- `CWSendStr`
- `SetBufPTT`
- `SendCW`

It also accepts generic `<PortNr>` / `<Value>` command roots such as `SetWPM`,
`Tune`, `TuneStop`, `Reset`, `PortOpen`, `RTSEnable`, `DTREnable`, and
`WinkeyPutChar`.
