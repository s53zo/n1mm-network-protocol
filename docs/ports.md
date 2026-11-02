# Ports and Options

The integration paths below were inspected statically in the supplied application
assemblies `1.0.11364.0` and `1.0.11469.0`. A listed listener is conditional on
its feature being enabled; these are not measurements of open ports. See
[integration behavior](integrations.md) for formats, version differences, and
limits.

## Port Matrix

| Port | Protocol | Direction | Purpose | Configurability |
| ---: | --- | --- | --- | --- |
| `12070` | TCP | inbound and outbound | Multi-user station synchronization, `DATA__...__DATA` frames. | Local listener is fixed on `12070`; peer port normally defaults to `12070`, with station-specific overrides possible. |
| `12070` | UDP | inbound and outbound | Multi-user discovery advertisements. | Native discovery listener and normal LAN broadcast destination use `12070`; the advertised TCP peer port is separate. Tailscale sends use the station port. |
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
| `2240` | UDP | local bind / outbound | WSJT/JTDX messenger socket for interface 1; replies go to the endpoint learned from received UDP. | Fixed local source port; not the destination port. |
| `2241` | UDP | local bind / outbound | WSJT/JTDX messenger socket for interface 2; replies go to the endpoint learned from received UDP. | Fixed local source port; not the destination port. |
| `52001` | TCP | inbound | External logging TCP listener for WSJT/JTDX interface 1. | Configurable IP/port and enable setting. |
| `52006` | TCP | inbound | External logging TCP listener for WSJT/JTDX interface 2. | Configurable IP/port and enable setting. |
| `52002` | TCP | inbound | WSJT/JTDX radio-control listener for radio 1. | Fixed loopback listener. |
| `52004` | TCP | inbound | WSJT/JTDX radio-control listener for radio 2. | Fixed loopback listener. |
| `61002` | TCP | inbound | WSJT/JTDX JTTY mode listener for radio 1. | Fixed loopback listener, passed to WSJT/JTDX as `--n1mm-tcp-port 61002`. |
| `61004` | TCP | inbound | WSJT/JTDX JTTY mode listener for radio 2. | Fixed loopback listener, passed to WSJT/JTDX as `--n1mm-tcp-port 61004`. |
| `52301`, `52303` | TCP | unconfirmed | Previously documented MMTTY special-case ports. | No listener setup for these ports was established in the inspected builds; do not treat these as confirmed open-port requirements. |
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
The destination and `Broadcast*Addr` lists are separated by spaces. Spectrum
relay and SDR server lists instead use commas.

`IsBroadcastContact` and `IsBroadcastAllQsos` are stored non-realtime options.
The effective `IsBroadcastContact()` and `IsBroadcastAllQsos()` checks also
return true while RTC realtime scoring is enabled, even when those stored
options are false.

## WSJT/JTDX Address Settings

| Setting | Interface 1 default | Interface 2 setting / default |
| --- | --- | --- |
| UDP reader port | `WSJTJTDXUDPPort`: `2237` | `WSJTJTDXUDPPort2`: `2239` |
| UDP address | `WSJTJTDXUDPIP`: `127.0.0.1` | `WSJTJTDXUDPIP2`: `127.0.0.1` |
| Logging TCP address | `ExternalLoggingTCPIP`: `127.0.0.1` | `ExternalLoggingTCPIP2`: `127.0.0.1` |
| Logging TCP port | `ExternalLoggingTCPPort`: `52001` | `ExternalLoggingTCPPort2`: `52006` |

The UDP reader binds the configured port on all IPv4 interfaces; its address
setting is not a loopback bind restriction. Addresses beginning with `224` or
`239` select a multicast join on an `IPAddress.Any` socket. Other addresses use
the port-only UDP client constructor. The logging TCP listener binds the
configured IP address explicitly. These paths are enabled separately.

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
