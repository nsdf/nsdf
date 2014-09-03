# fixed, uncompressed
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -d oned &> profile_out_ONED_fixed_uncompressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.ONED_fixed_uncompressed.lprof
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -d vlen &> profile_out_VLEN_fixed_uncompressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.VLEN_fixed_uncompressed.lprof
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -d nan &> profile_out_NAN_fixed_uncompressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.NAN_fixed_uncompressed.lprof

# fixed, compressed
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -c -d oned &> profile_out_ONED_fixed_compressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.ONED_fixed_compressed.lprof
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -c -d vlen &> profile_out_VLEN_fixed_compressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.VLEN_fixed_compressed.lprof
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -c -d nan &> profile_out_NAN_fixed_compressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.NAN_fixed_compressed.lprof

# incremental, uncompressed
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -i 1024 -d oned &> profile_out_ONED_incremental_uncompressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.ONED_incremental_uncompressed.lprof
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -i 1024 -d vlen &> profile_out_VLEN_incremental_uncompressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.VLEN_incremental_uncompressed.lprof
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -i 1024  -d nan &> profile_out_NAN_incremental_uncompressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.NAN_incremental_uncompressed.lprof

# incremental, compressed
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -i 1024  -c -d oned &> profile_out_ONED_incremental_compressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.ONED_incremental_compressed.lprof
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -i 1024  -c -d vlen &> profile_out_VLEN_incremental_compressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.VLEN_incremental_compressed.lprof
kernprof -l -v ~/src/nsdf/benchmark/benchmark_writer.py -i 1024  -c -d nan &> profile_out_NAN_incremental_compressed.txt
mv benchmark_writer.py.lprof benchmark_writer.py.NAN_incremental_compressed.lprof

