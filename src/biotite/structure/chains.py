# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

"""
This module provides utility for handling data on chain level, rather than
atom level.
"""

__name__ = "biotite.structure"
__author__ = "Patrick Kunzmann"
__all__ = ["get_chain_starts", "get_chains", "get_chain_count", "chain_iter"]

import numpy as np


def get_chain_starts(array):
    """
    Get the indices in an atom array, which indicates the beginning of
    a new chain.
    
    A new chain starts, when the chain ID changes.

    This method is internally used by all other chain-related
    functions.
    
    Parameters
    ----------
    array : AtomArray or AtomArrayStack
        The atom array (stack) to get the chain starts from.
        
    Returns
    -------
    starts : ndarray, dtype=int
        The start indices of new chains in `array`.
    
    See also
    --------
    get_residue_starts
    """
    chain_ids = array.chain_id
    chain_changes = np.where((chain_ids[:-1] != chain_ids[1:]))[0] + 1
    chain_starts = np.append([0], chain_changes)
    return chain_starts


def get_chains(array):
    """
    Get the chain IDs of an atom array (stack).
    
    The chains are listed in the same order they occur in the array
    (stack).
    
    Parameters
    ----------
    array : AtomArray or AtomArrayStack
        The atom array (stack), where the chains are determined.
        
    Returns
    -------
    ids : ndarray, dtype=str
        List of chain IDs.
        
    See also
    --------
    get_residues
    """
    return array.chain_id[get_chain_starts(array)]


def get_chain_count(array):
    """
    Get the amount of chains in an atom array (stack).
    
    The count is determined from the `chain_id` annotation.
    Each time the chain ID changes, the count is incremented.
    
    Parameters
    ----------
    array : AtomArray or AtomArrayStack
        The atom array (stack), where the chains are counted.
        
    Returns
    -------
    count : int
        Amount of chains.
    
    See also
    --------
    get_residue_count
    """
    return len(get_chain_starts(array))


def chain_iter(array):
    """
    Iterate over all chains in an atom array (stack).
    
    Parameters
    ----------
    array : AtomArray or AtomArrayStack
        The atom array (stack) to iterate over.
        
    Returns
    -------
    count : generator of AtomArray or AtomArrayStack
        A generator of subarrays or substacks (dependent on the input
        type) containing each chain of the input `array`.
    
    See also
    --------
    residue_iter
    """
    # The exclusive stop is appended to the chain starts
    starts = np.append(get_chain_starts(array), [array.array_length()])
    for i in range(len(starts)-1):
        yield array[..., starts[i] : starts[i+1]]