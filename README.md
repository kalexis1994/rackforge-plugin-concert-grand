# RackForge Concert Grand

Physically modelled piano, distributed as an independent RackForge plugin.
Current package: **0.171.37**, ID `org.rackforge.concert-grand`.

The DSP, Web interface, programs, artwork, model tests, render tools and
laboratory reports belong here. RackForge owns the portable SDK and host;
the supported SDK is pinned to a published Git commit in Cargo.toml.

## Build and test

```sh
cargo test --locked --release -p rackforge-concert-grand --lib -- --test-threads=1
cargo test --locked --release -p rackforge-concert-grand --lib render_fingerprint -- --ignored --test-threads=1
rustup target add wasm32-unknown-unknown
cargo build --locked --release --target wasm32-unknown-unknown -p rackforge-concert-grand
```

Run tests with one thread: model knobs are process-wide atomics. The repository
configures the required native stack and SIMD128/8 MiB WebAssembly stack.
Native render fingerprints for the factory voicing are
`3a1123cb1d7fff23` and `19c7880b54509648`.

Optional tools:

```sh
cargo run --release --features lab --example lab -- --list
cargo test --release --features host-tests --tests -- --test-threads=1
cargo run --release --features host-tests --example wasm-tax -- PACKAGE_DIRECTORY
```

The native laboratory is Windows-specific. Host integration tests require
RackForge's runtime dependencies and an already-built component.

## Package

Keep the published RackForge checkout beside this one, or set `RACKFORGE_ROOT`.
It supplies the validated `rackforge-store` packer, not the piano's source.

```sh
python tools/build-package.py --output artifacts/RF-Concert-Grand.rfplugin
```

Pass `--component PATH` to reuse a verified component and repeat
`--native linux-aarch64=PATH_TO_LIBRARY` for native portable builds. The package
always contains the component; hosts choose a native build on supported
platforms. Verify every native build with `rackforge-core compare-native`
against that same component before publishing it.

Releases attach `RF-Concert-Grand.rfplugin` and a SHA256 file to tag
`v<package-version>`. RackForge consumes a specific release URL and checksum;
its build no longer compiles this repository. Published assets must remain
immutable: any change gets a new package version and a new host pin.

## Listening profile

The accepted version C renders of the Nocturne and La Campanella use Concert,
44.1 kHz and blocks of 256 frames. The factory voicing uses `RADIATION_RATE=2.55`,
`MERGE_RAMP_S=0.004` seconds and Hammer Hard at `0.51`. It also halves the
gain of the free-string bank (`UNDAMPED_MIX=1.125`) to moderate the bell-like
ring heard on G4. The model knobs share these defaults across the factory
bank. Each preset inherits Hammer Hard from Concert unless it sets its own
value, as Player Upright does. Existing states keep their saved settings.

The latest listening profile smooths modal overlap and bridge-position contrast
through the middle of the soundboard, uses weighted unison leverage at the
bridge, and progressively restores the higher free-string modes. The gain
transition is tied to the bank's frequency reference, so the G4/G6 resonance
remains moderated while C6 recovers its release tail.

With partial sustain, a released key gives its felt time to reach the string
before applying the pressure left by the rail. Pedal changes during that
travel update the pending pressure.
Partial pressure uses the same vertical and horizontal grip as a fully
seated felt. The reference factor stays fixed until the pressure is released.

Research tools use `RACKFORGE_ROOT` for SDK/tool sources and keep generated
renders, caches and external reference recordings under ignored `local/`.
Historical JSON measurements keep their original absolute paths and hashes.
