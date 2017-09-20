#! /usr/bin/env python
import numpy as np
import sys
    
def delete_column(fskymodel, col_to_delete):
    new_model=[] #store the altered model ready to write to file.
    
    #Fetch the filtered skymodel
    with open(fskymodel) as f:
        g=f.readlines()
        
    #First check whether the column is actually there, return if not.    
    if col_to_delete not in g[0]:
        logger.error("LogarithmicSI column could not be found! The skymodel was not changed.")
        return False
    #Now we need to remove the column but also account for the possibility of a multi-component SpectralIndex
    else:
        split_format=g[0].rstrip().split(",")       #Split the format line by commas
        num_cols=len(split_format)                  #Obtain what the length of each source should be
        del_col_index=[i for i,j in enumerate(split_format) if col_to_delete in j][0]   #Find the index of LogarithmicSI column
        si_col_index=[i for i,j in enumerate(split_format) if "SpectralIndex" in j][0]  #Find the index of the SpectralIndex column
        #Remove the LogarithmicSI column from the format header and append to new_model
        del split_format[del_col_index]
        new_model.append(split_format)
        #Now loop through the sources
        for source in g[1:]:
            source_split=source.rstrip().split(",")     #Split by comma again
            source_len=len(source_split)
            if source_len==num_cols:
                #The source has the expected number of columns. Great! It can be stored.
                del source_split[del_col_index]
                new_model.append(source_split)
            
            #A check that the source is not shorter as this would break things (should never be the case)
            elif source_len < num_cols:
                logger.error("Source {} is strange! Skipping!".format(source_split[0]))
                continue
            
            #If it's longer, the difference means we have an extra DIFF number of SI components.
            elif source_len > num_cols:
                diff=source_len-num_cols    #Find the diff value
                si=[source_split[i] for i in range(si_col_index, si_col_index+diff+1)]  #Gather all the SI components into one list.
                truesi=",".join(si)         #Generate the True Spec Index component by combining those obtained above.
                #Sanity check that it starts with [ and ends with ]
                if truesi.startswith("[") and truesi.endswith("]"):
                    pass
                else:
                    #Just skip if something is wrong.
                    logger.error("SpectralIndex doesn't seem correct. Skipping {}!.".format(source_split[0]))
                    continue
                #Now we have the trueSI component the index is set as this value.
                source_split[si_col_index]=truesi
                #Now remove the extra DIFF SI columns
                for i in range(diff):
                    del source_split[si_col_index+1] #Column falls back to the same number when deleting, hence no need to change the index
                #Finally not forgetting to actually remove the LogarithmicSI column, and store.
                del source_split[del_col_index]
                new_model.append(source_split)
    
    new_model=np.array(new_model)       #convert to numpy array
    # print new_model
    #Write the new skymodel (it overwrites)
    np.savetxt(fskymodel, new_model, delimiter=",", fmt='%s')      #save the new skymodel replacing the old one
    return True


def main(ms,skymodel,maskname,skymodel_cut,scripts,keep_in_beam=True,delete_LogSI_column=False):
    
    sys.path.append(scripts)
    from lib_pipeline import *

    # make beam
    phasecentre = get_phase_centre(ms)
    make_beam_reg(phasecentre[0], phasecentre[1], 8, 'beam.reg')
    
    # prepare mask
    blank_image_reg(maskname, 'beam.reg', inverse=keep_in_beam, blankval=0) # if keep_in_beam set to 0 everything outside beam.reg

    # apply mask
    logger.info('Predict (apply mask)...')
    lsm = lsmtool.load(skymodel)
    lsm.select('%s == True' % maskname)
    fluxes = lsm.getColValues('I')
    #lsm.remove(np.abs(fluxes) < 5e-4) # TEST
    lsm.write(skymodel_cut, format='makesourcedb', clobber=True)
    del lsm
    #Fix for old makesourcedb
    if delete_LogSI_column:
            logger.info("Attempting to delete the 'LogarithmicSI' column from the sky model...")
            success=delete_column(skymodel_cut, 'LogarithmicSI')
            if success:
                logger.info("LogarithmicSI column successfully deleted.")
            else:
                logger.error("Error occurred when trying to delete LogarithmicSI column. Model not changed.")
    pass


########################################################################
if __name__ == '__main__':
  
    import argparse
    from argparse import RawTextHelpFormatter
    
    descriptiontext = "Filter a CC model with a given mask.\n"
    parser = argparse.ArgumentParser(description=descriptiontext, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('--ms', type=str, nargs='+', help='Input MS')
    parser.add_argument('--output', type=str, nargs='+', help='Output BBS skymodel')
    parser.add_argument('-m','--mask', nargs='+', type=str, help='A mask to filter input CC model')
    parser.add_argument('-s','--skymodel', nargs='+', type=str, help='Input BBS skymodel')
    parser.add_argument('-S','--scripts', nargs='+', type=str, help='Directory of pipeline scripts')
    parser.add_argument('-x','--delete-LogSI-col', action='store_true', help="Remove the 'LogarithmicSI' column from the sky model")

    args = parser.parse_args()

    main(ms=args.ms,skymodel=args.skymodel,maskname=args.mask,skymodel_cut=args.output,scripts=args.scripts, delete_LogSI_column=args.removeLogSIcol) #delete LogSI required for old makesourcedb.
    
    pass