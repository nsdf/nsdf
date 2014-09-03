# Run cprofile for profiling the benchmark writer
# Author: Subhasis Ra, Date: Wed Sep  3 20:28:31 IST 2014

# fixed, uncompressed
python -m cProfile -o ONED_fixed_uncompressed.prof benchmark_writer.py -m 100000 -n 200000 -d oned &> profile_out_ONED_fixed_uncompressed.txt
python -m cProfile -o VLEN_fixed_uncompressed.prof benchmark_writer.py  -m 100000 -n 200000 -d vlen &> profile_out_VLEN_fixed_uncompressed.txt
python -m cProfile -o AN_fixed_uncompressed.prof benchmark_writer.py  -m 100000 -n 200000 -d nan &> profile_out_NAN_fixed_uncompressed.txt

# fixed, compressed
python -m cProfile -o ONED_fixed_compressed.prof benchmark_writer.py -c  -m 100000 -n 200000 -d oned &> profile_out_ONED_fixed_compressed.txt
python -m cProfile -o VLEN_fixed_compressed.prof benchmark_writer.py -c  -m 100000 -n 200000 -d vlen &> profile_out_VLEN_fixed_compressed.txt
python -m cProfile -o NAN_fixed_compressed.prof benchmark_writer.py -c  -m 100000 -n 200000 -d nan &> profile_out_NAN_fixed_compressed.txt

# incremental, uncompressed
python -m cProfile -o ONED_incremental_uncompressed.prof benchmark_writer.py -i 1000  -m 100000 -n 200000 -d oned &> profile_out_ONED_incremental_uncompressed.txt
python -m cProfile -o VLEN_incremental_uncompressed.prof benchmark_writer.py -i 1000  -m 100000 -n 200000 -d vlen &> profile_out_VLEN_incremental_uncompressed.txt
python -m cProfile -o NAN_incremental_uncompressed.prof benchmark_writer.py -i 1000   -m 100000 -n 200000 -d nan &> profile_out_NAN_incremental_uncompressed.txt

# incremental, compressed
python -m cProfile -o ONED_incremental_compressed.prof benchmark_writer.py -i 1000  -c  -m 100000 -n 200000 -d oned &> profile_out_ONED_incremental_compressed.txt
python -m cProfile -o VLEN_incremental_compressed.prof benchmark_writer.py -i 1000  -c  -m 100000 -n 200000 -d vlen &> profile_out_VLEN_incremental_compressed.txt
python -m cProfile -o NAN_incremental_compressed.prof benchmark_writer.py -i 1000  -c  -m 100000 -n 200000 -d nan &> profile_out_NAN_incremental_compressed.txt

