"""Console-mode EXE required so Chrome/Firefox receive binary stdio handles."""
if __name__=='__main__':
    from host.native import main
    main()
