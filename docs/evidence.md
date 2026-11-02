# Static Verification Record

Review date: 2026-11-02. Scope: networking behavior documented by this repository,
using the two author-authorized installers supplied in `~/Downloads`.
No installer or N1MM application was executed, no station traffic was sent, and
no contest database was modified. Runtime interoperability remains untested.

## Artifact Identity

| Installer | SHA-256 |
| --- | --- |
| `N1MM-Logger-FullInstaller-1.0.11364.exe` | `f35d86ff752538791724371667adf956e8781be3b731dbe62c71a502f86c6d71` |
| `N1MM-Logger-Update-1.0.11469.exe` | `4e4116de3c1d982307a39f25203eb6138f49a7b3a3e49114978fe604fcf35ca5` |

Both are NSIS packages. Extraction with Docker-hosted 7-Zip produced 60 files
from the full package and 30 from the update, including installer helper files.
These are extracted-payload counts, not claims about the final installed tree.

| Package / assembly | Assembly version | SHA-256 | Module MVID |
| --- | --- | --- | --- |
| Full / `N1MMLogger.net.exe` | `1.0.11364.0` | `8a23ac87aa740cb691696ad8fc992c4bec9dcc9259cef74c7379423de9317d1c` | `ceb898ba-458b-4d06-b723-8aefee98fbf1` |
| Update / `N1MMLogger.net.exe` | `1.0.11469.0` | `b43a4e8fe03a17046b44af16da4eb18d7fb24a459e9ad8957d3b5f713e772abc` | `c0120c96-5116-40ad-a671-5d02c8a9ef0f` |
| Full / `N1MMLibrary.dll` | `1.0.11355.0` | `d0d5958f36a613152fb43cba0d9015407385c536adffaa66179c494bac207170` | `866fcaec-f1bb-4f29-96e4-9c18917989db` |
| Update / `N1MMLibrary.dll` | `1.0.11466.0` | `e632d9ecf72c75ba31e243de4e9cefd249a0a1eb55453ff9738ac0891f5590c9` | `dc3512cd-ab8f-4cbb-85fe-c323e6a6cb91` |
| Full / `N1MMRotor.Net` | `1.0.11364.0` | `4bd2548bb1d288b1ca1d96601dc5441e5ebc704c0eeb6acf7a185563e8de6555` | `9bd7d533-8931-4a89-9957-eb27eb0286dd` |
| Full / `N1MMSDRServer` | `1.0.11364.0` | `2b89ccf4b85acfbcc64942d49158706b61d6ade5ca2394965918de1f74946e14` | `4e6f6cdc-9c3c-4acc-80c2-b0699d3f3e10` |
| Update / `N1MMRotor.Net` | `1.0.11469.0` | `500f0ce0227da83c247f8f0b45333b126e0c07f0a711beaba480a6eb8ff44b83` | `f5931c65-9a8c-4641-ba2c-a02912fc0bac` |
| Update / `N1MMSDRServer` | `1.0.11469.0` | `96b2dd30211f39bf12a76851dd16219423abd4efa16ee10c14ae42d4f1bed914` | `295576fd-7b7f-451b-9493-5d50cfa271ea` |

The update contains complete replacement main/library assemblies, so networking
CIL can be inspected without applying a binary delta. It is not a standalone
installation: main-assembly references `ObjectListView`, `AxInterop.MMVARILib`,
and `AxInterop.XMMTLib` are absent from its payload but present in the full
package. The full package additionally supplies OCX/native helpers, resources
and the .NET 4.6 prerequisite installer. Both main assemblies declare x86,
IL-only .NET Framework 4.6 code and 25 assembly references. Framework assemblies
and installed COM prerequisites were not resolved or executed. Dependency
inventory supports the need for an existing/full installation; installer
registry changes, registration and upgrade sequencing were not executed.

## Tools and Retained Evidence

REA `6.8.0` performed execution-free PE/CLI identity and selected-member/CIL
inspection. Its MCP tools were not exposed in the active session; the supported
REA CLI was used without changing client configuration. ILSpy `9.1.0.7988`,
inside local Docker (`mcr.microsoft.com/dotnet/sdk:8.0`), supplied readable C#
reconstruction of selected classes. Decompiled text is not original VB source
and was not used to claim a successful rebuild.

All extracted binaries, reconstructed code and bulky evidence are retained
outside this repository at `/Users/simon/n1mm-analysis/`:

- `evidence/payload-manifest.json`: every extracted file's size and SHA-256.
- `evidence/*-managed.json`: canonical REA main/library identities.
- `evidence/*-members.json`: selected-member evidence bundles, including CIL
  anchors and build-local metadata tokens; `method-anchors.json` indexes core
  methods without copying source into the repo.
- `evidence/{commands,station,integrations}-findings.md`: detailed method/line
  anchors, comparison scope, corrections and remaining uncertainties.
- `decompiled/{full,update}/`: selected class exports, not committed source.
- `tools/`: extraction/decompilation tooling and scripts.

Canonical REA records below are retained in those JSON files. Tokens are valid
only with the artifact SHA-256 and MVID; they are not cross-version identifiers.

| Evidence file | REA evidence ID | Scope |
| --- | --- | --- |
| `full-managed.json` | `ev_d4acf5b27f02a5d61f9cc6481faaf487bffffc971d983bc7281a1ba43c6fe35c` | Full main assembly identity |
| `update-managed.json` | `ev_3c81b2fb4e97c6ffedd59bcb836cacdc35ff876a2cfe7c7cc343991490224c46` | Update main assembly identity |
| `full-library-managed.json` | `ev_09105dd6c2acfbd41b69419881276c06d3e6393d78a6285cb65588b0658d6230` | Full library identity |
| `update-library-managed.json` | `ev_58749f209817a97fce1b0ff5aeec29060fb9d20c57751f4bdb316b71d97bd610` | Update library identity |
| `full-network-members.json` | `ev_02695317956bea2894a78fb22b5aa749bf0dfff55128389b0c62647d6d5aa3a3` | Full MultiStation/MultiOpManager/UDPClass/AsyncTcpClient/AsyncTcpListener |
| `update-network-members.json` | `ev_247a38b8d4abfb96e212ad2924cf18878c01ea45095c4cf46159e59b8bacd832` | Update MultiStation/StationClass/UDPClass/AsyncTcpClient/AsyncTcpListener |
| `update-multiop-members.json` | `ev_c26484bf9f698023b6d1c7c6347117a0be56e144bc53cae8d7576d8e44066f0e` | Update MultiOpManager |
| `update-integrations-members.json` | `ev_fd8feef2519005dcc894cff41a33210e2a27425edfabd492e5875fe26beac123` | Update N1MMInterface/WSJTCode/WSJTRadio/TCPRadio/RotorManager |
| `update-sync-members.json` | `ev_1cdf342f817c16cb58ce71889ee2a1cefb18c5045f6920d7903db6f800cb7e84` | Update Contact/DBSupport/CRC32Module |
| `full-rotor-managed.json` | `ev_f26309b2cfe10b4f1fd89189923e82db9a7adcc0c334d9c3c297696a709946ea` | Full rotor companion identity |
| `full-sdr-managed.json` | `ev_349f799c31bbaf6efec2ebd9701d951338febfa6fb9f1eef2c146a591f45c097` | Full sdr companion identity |
| `update-rotor-managed.json` | `ev_233fdc01320496dec7138e805bd9d06bd3a718eca24c953a9f0006e5aa06b7e0` | Update rotor companion identity |
| `update-sdr-managed.json` | `ev_d647d1d93510b5d83965b7ff5cf17cbdf342031bc1b767cb869be974051a892b` | Update sdr companion identity |

The initial whole-main member request (`update-members-bundle.json`,
`ev_2502e180cb815ebf5c89709819be53729b682a075f3ee6ebc34bdf521456edf3`)
reached capacity after admitting the type inventory. Its empty member
collections do not prove absence. Subsequent selections above completed their
reported coverage. Class selection and static call anchors do not establish
whole-program behavioral coverage.

## Findings and Method Anchors

Behavioral descriptions derive from reading reconstructed method bodies,
corroborated by REA identities, declarations, CIL/string anchors where collected.
They are confirmed static code paths, not observations of execution.
Class names below are in `N1MMLogger.Net` unless stated otherwise.

| Topic | Methods inspected | Result / repository destination |
| --- | --- | --- |
| Discovery | MultiOpManager.HandleUDPMessage, CreateOrGetMultiStationForNetBiosName; N1MMInterface.ThreadedBroadcastNetBiosName, SendNetBiosBroadcast | Exact version match; UDP source IP used; default writer `12070`; sender UTF-8/receiver ASCII; per-interface beacon source. [Protocol](protocol.md) |
| TCP lifecycle/framing | MultiOpManager.ServerThread, DispatchDataFromTcpClient, DispatchDataFromString, CloseAll; MultiStation.OpenWriterConnection, SendData, ReadCallback, DataArrivalQueing | Paired writers/readers; initial ASCII decode; established UTF-8; `~` delimiter and native buffering constraints. Replies use outgoing half. [Protocol](protocol.md) |
| Liveness | MultiStation.IsWorking, DataArrivalProcessing; MultiOpManager.SendEchoReq | Remote working state is less than 20 seconds since processed-message timestamp; echo copies local-date/time fields. Native timer cadence not established. [Implementation](implementation-notes.md) |
| Commands/state | MultiStation.DataArrivalProcessing, StatusString; MultiOpManager.SendStatus, SendIAM, SendFreq, SendQSONrs | 45 admitted commands; 17 STATUS fields; targeted versus broadcast response distinctions. [Commands](commands.md) |
| Contact/log sync | Contact.QSOString; DBSupport.ComputeCheckSum, SetOfQs, SendQs, DeleteQsFor; CRC32Module.CRC32; N1MMLoggerCommon.SetNewContact, NewLogQSO | 43 contact fields, exact-version/contest gates, half-open SQL windows, signed CRC over database text, original-copy restrictions. [Commands](commands.md#checksum-and-log-repair) |
| XML/rotor/SDR | N1MMInterface.Initialize, HandleUDPMessage, NewGoAzi, NewStopRotor; UDPClass.DistributeXml, HandleGenericMessage; RotorManager.HandleRotorUDPMessage; AbstractSpectrumProcessing.GetBroadcastDataString; WaterfallBandmapSpectrumProcessing.SendSpectrumCmd, GetExtIOParms | Port settings, XML routing, rotor tenths of degrees, relay/server destinations. [Integrations](integrations.md) |
| WSJT/JTDX/JTTY | WSJTCode.Initialize, LoggingTCPListening, processMsg; WSJTRadio.WorkProcesser, SetExternalTCPCommands, ParseTcpMessage; RadioInterface.Frequency | Framed logging ACK precedes import; kHz query formatting; tagged parameter bodies; chunk-buffer limitations. [Examples](payload-examples.md) |
| MMTTY/CAT | DigitalInterface.ProcessMMTTYData; TCPRadio; AsyncTcpClient/AsyncTcpListener | Marker handler confirmed; previously listed `52301`/`52303` listener setup unconfirmed; CAT is a separate transport. [Ports](ports.md) |
| Six-NUL bytes | MultiStation.SendData/ReadCallback; N1MMLibrary.SharedLib.IsConnected/CloseTcpClientConnection; N1MMTcpClient tracing helpers | No required six-NUL sender/ACK found in these paths. Historical traffic claim remains uncorroborated. Experimental option retained, not enabled. |

## Version Comparison Boundary

The two `MultiOpManager` reconstructions are textually identical. Compared
command processing, contact serialization and selected checksum/database
methods also reconstruct identically. This supports those selected paths only,
not binary identity, unchanged dependencies or whole-program equivalence.

In the newer MultiStation, receive queueing has an explicit instance buffer and
lock; writer error handling checks socket error codes; reader-start error
handling changes. Adjacent differences include case-insensitive Spectrum source
matching, JTTY CALLSIGN support, WSJT callsign transition handling, SDR display
rate/shutdown behavior and Tailscale executable lookup. Details and limits are
in [integrations.md](integrations.md#observed-version-differences).

## Validation and Remaining Unknowns

Validation: `python3 -m unittest discover -s tests` passed all **37 tests**;
`git diff --check` passed. The saved run is `evidence/final-tests.log` in the
external analysis directory. All 90 extracted-file hashes and eight assembly
identity records were checked against retained evidence, and local documentation
links were checked.

Three independent SWE audits reviewed transport/concurrency, protocol/tests, and
documentation/evidence. Follow-up fixes make connection registration atomic with
publication and shutdown checks, discard frames following a disconnect, reject
non-ASCII station numbers, bind outbound TCP to the discovery source address,
and distinguish WSJT wire magic from ASCII-decoded text. Regression tests cover the implementation fixes. The existing static
uncertainties remain unchanged.

Python tests exercise split/coalesced UTF-8 frames and marker fragments, NUL/noise
discard, paired reply routing, delayed outbound links, request fields and
recipient scope, partial writes, discovery source binding, disconnect and
shutdown. All tests use synthetic input and fake sockets/mocks; they do not
establish live N1MM compatibility. Payload examples were checked for field
counts and declared command/parameter lengths.

The Python example does not implement log synchronization, station-number or
serial allocation, multiple stations sharing one IP, or VPN/Tailscale emulation.
Its advertised-address/port peer selection is sample policy; it is different
from the inspected native discovery path. Shutdown notification is best effort
under socket backpressure. The companion SDR/rotor networking receivers were also inspected in selected
classes; their identities above bind those findings separately from the logger.
No native heartbeat timer cadence, actual enabled
listener set, non-ASCII CRC compatibility, radio effects or installer upgrade
execution was verified. No sender for the three receiver-only commands was
found in the selected networking senders; this is a bounded search. MMTTY port
setup and six-NUL origin remain unresolved from this static evidence.
