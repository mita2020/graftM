#!/usr/bin/env python

from graftm.Messenger import Messenger

import os
import shutil 
from test.test_MimeWriter import OUTPUT
import IPython

# Constants - don't change them evar.
FORMAT_FASTA = 'FORMAT_FASTA'
FORMAT_FASTQ_GZ = 'FORMAT_FASTQ_GZ'

class HouseKeeping:
    
    def make_filter_directories(self, filter_list, input_list, force):
        
        output_hash = {}     
        
        for sequence_file in input_list:
            
            base_sequence = os.path.basename(sequence_file).split('.')[0]
            
            if force:
                shutil.rmtree(base_sequence, ignore_errors=True)
            
            try:
                os.mkdir(base_sequence)
            except:
                Messenger().header('Directory %s already exists. Exiting to prevent over-writing\n' % base_sequence)
                exit(1)    
            
            output_hash[sequence_file] = {'dir': base_sequence}
            
            for f in filter_list:
                base_filter = os.path.basename(f.split('.')[0])
                filter_output = os.path.join(base_sequence, base_filter)
                os.mkdir(filter_output)
                output_hash[sequence_file][base_filter+ '.hmm'] = filter_output
            
        return output_hash
        
        
    def read_contents(self, gpkg_path):
        
        c = os.path.join(gpkg_path, "contents.txt")
        
        contents_hash = {}
        
        f =  [x.rstrip() for x in open(c, 'r').readlines()]
        
        for entry in f:
            s = entry.split('=')
            contents_hash[s[0]] = s[1].split(',')
        
        contents_hash['HMM'] = [os.path.join(gpkg_path, x) for x in contents_hash['HMM']]
        return contents_hash
        
        
    # Given a Return the guessed file format, or raise an Exception if
    def guess_sequence_input_file_format(self, sequence_file_path):
    
        if sequence_file_path.endswith(('.fa', '.faa', '.fna')):  # Check the file type
            return FORMAT_FASTA
    
        elif sequence_file_path.endswith(('.fq.gz', '.fastq.gz')):
            return FORMAT_FASTQ_GZ
    
        else:
            raise Exception("Unable to guess file format of sequence file: %s" % sequence_file_path)
    
    def setpipe(self, hmm):
        t = [x.rstrip() for x in open(hmm, 'r').readlines() if x.startswith('ALPH')][0].split()[1]
        
        if t == 'DNA':
            return 'D'
        elif t == 'amino':
            return 'P'
        else:
            print Messenger().error_message('Unrecognised HMM library. Not sure which pipeline to use.')
            exit(1)
    
    def delete(self, delete_list):
        for item in delete_list:
            try:
                os.remove(item)
                
            except:
                pass
    
    def make_working_directory(self, directory_path, force):
        if force:
            shutil.rmtree(directory_path, ignore_errors=True)
            os.mkdir(directory_path)
       
        else:
            try:
                os.mkdir(directory_path)
                    
            except:
                Messenger().header('Directory %s already exists. Exiting to prevent over-writing\n' % directory_path)
                exit(1)    
        
    def parameter_checks(self, args):
        # --- Check parameters are in sensible land
        # Check that the necessary files are in place
        
        if args.subparser_name == 'graft':
        
            if hasattr(args, 'hmm_file') and not hasattr(args, 'reference_package'):
                Messenger().message('\nA reference package needs to be specified\n')
                exit(1)
            
            
            elif hasattr(args, 'reference_package') and not hasattr(args, 'hmm_file'):
                Messenger().message('A HMM file needs to be specified\n')
                exit(1)           
                    
            # Check that the placement cutoff is between 0.5 and 1
            if float(args.placements_cutoff) < float(0.5) or float(args.placements_cutoff) > float(1.0):
                Messenger().message('Please specify a confidence level (-d) between 0.5 and 1.0! Found: %s' % args.placements_cutoff)
                exit(1)
    
            # Set string for hmmsearch evalue
            args.eval = '-E %s' % args.eval
    
            # Determine the File format based on the suffix
            input_file_format = self.guess_sequence_input_file_format(args.forward)
            sequence_file_list = []
            if hasattr(args, 'reverse'):
                fors = args.forward.split(',')
                revs = args.reverse.split(',')
                
                for i in range(0, len(fors)):
                    sequence_file_list.append([fors[i], revs[i]])
                
            elif not hasattr(args, 'reverse'):
                for f in args.forward.split(','):
                    f = [f]
                    sequence_file_list.append(f)
                    
            else:
                Messenger().error_message('Confusing input. Did you specify the same amount of reverse and forward read files?')
            
                
            return sequence_file_list, input_file_format
        
        elif args.subparser_name == 'filter':
            input_file_format = self.guess_sequence_input_file_format(args.reads)
            sequence_file_list = args.reads.split(',')
            return sequence_file_list, input_file_format
    
        


    def reset_outdir(self, args, base):
        # reset working directory
        setattr(args, 'output_directory', base) 
        
        # create the directory
        self.make_working_directory(args.output_directory, args.force)
        
        
    def set_attributes(self, args):  
        
        # Read graftM package and assign HMM and refpkg file
           
        if hasattr(args, 'graftm_package'):
                
            for item in os.listdir(args.graftm_package):
                    
                if item.endswith('.hmm'):
                    setattr(args, 'hmm_file', os.path.join(args.graftm_package, item))
                        
                elif item.endswith('.refpkg'):
                    setattr(args, 'reference_package', os.path.join(args.graftm_package, item))
            
            
        if not hasattr(args, 'reference_package') or not hasattr(args, 'hmm_file'):
            Messenger().error_message('%s is empty or misformatted.' % args.graftm_package)
            exit(1)
            