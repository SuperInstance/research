fn main() {
    let mut b = cc::Build::new();
    b.std("c99").include("include").files(&[
        "src/engine.c", "src/proof.c", "src/route.c",
        "src/crdt.c", "src/world.c", "src/time.c", "src/quf.c",
    ]);
    b.compile("quilt_c");
    println!("cargo:rerun-if-changed=src");
    println!("cargo:rerun-if-changed=include");
}
