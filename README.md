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
Native render fingerprints remain `e4abcfd02a5757c1` and `dfb7f193962235e0`.

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

The accepted Nocturne and Campanella renders use Concert, 44.1 kHz, 256 frames,
and public parameter 192 (`MERGE_RAMP_S`) set to **0.004 s**. The compiled default
remains zero for existing state compatibility. The deployment saves and restores
the explicit profile; see `docs/concert-grand-pi-2026-10-14`.

Research tools use `RACKFORGE_ROOT` for SDK/tool sources and keep generated
renders, caches and external reference recordings under ignored `local/`.
Historical JSON measurements keep their original absolute paths and hashes.
